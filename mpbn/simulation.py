
from itertools import combinations, chain
from multiprocessing import SimpleQueue, Process, current_process, cpu_count
import os

import numpy as np
from numpy.random import uniform, choice, seed
from scipy.special import binom

from mpbn import MPBooleanNetwork

from tqdm import tqdm

import re

BNET_SYMBOL_PAT = re.compile(r"[\w\.:]+")

class MPBNSim(MPBooleanNetwork):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, encoding="unate-dnf")
        g = self.influence_graph()
        self.deps = {}
        for i in g:
            self.deps[i] = {1: [], -1: []}
        for (j, i, d) in g.edges(data=True):
            self.deps[i][d["sign"]].append(j)
        for i in g:
            self.deps[i][0] = self.deps[i][1] + self.deps[i][-1]

        """
        boolean logic compilation
        """
        self.compiled_f = {}
        def repl_symbol(match):
            d = match.group(0)
            if d == "1":
                return "True"
            elif d == "0":
                return "False"
            else:
                return f"x['{d}']"
        for i, fi in self.items():
            fi_py = BNET_SYMBOL_PAT.sub(repl_symbol, str(fi))
            fi_py = fi_py.replace("!", "not ")
            fi_py = fi_py.replace("&", " and ")
            fi_py = fi_py.replace("|", " or ")
            self.compiled_f[i] = eval(f"lambda x: ({fi_py})")

    def local_eval(self, i, x):
        return self.compiled_f[i](x)

    LIM_MIN = [(1, 0), (-1, 1)]
    LIM_MAX = [(1, 1), (-1, 0)]
    def _lim_configuration(self, x, i, H, lim):
        y = x.copy()
        for (s, v) in lim:
            for j in self.deps[i][s]:
                if j in H:
                    y[j] = v
        return y
    def min_configuration(self, x, i, H):
        return self._lim_configuration(x, i, H, self.LIM_MIN)
    def max_configuration(self, x, i, H):
        return self._lim_configuration(x, i, H, self.LIM_MAX)


def can_flip(f, x, i, H, v):
    """
    return True iff there is a configuration z matching with x and H so that
    f[i](z) is different from v
    assumes f is locally monotone
    """
    v = bool(v)
    if v:
        z = f.min_configuration(x, i, H)
    else:
        z = f.max_configuration(x, i, H)
    return f.local_eval(i, z) != v

def spread(f, x, I, d):
    """
    return subset of I that can flip within the given depth d
    """
    H = set()
    I = set(I) # work on a mutable copy
    for _ in range(d):
        J = {i for i in I if can_flip(f, x, i, H, x[i])}
        H.update(J)
        I.difference_update(J)
        if not I or not J:
            break
    return H

def irreversible(f, x, H):
    """
    return subset of H that cannot flip back
    """
    return {i for i in H if not can_flip(f, x, i, H, 1-x[i])}

def reachable_spaces(f, x, depth):
    """
    a space is represented by a couple of sets of indices
        (H,L): H reversible flips, L irreversible flips
    """
    d = depth() if callable(depth) else depth
    S = [] # list of (index set, index set)
    I = frozenset(f) # set of indexes
    K = {I} # known
    Q = [I] # queue
    while Q:
        I = Q.pop(0)
        H = spread(f, x, I, d) # H is subset of I
        if not H:
            continue
        L = irreversible(f, x, H) if d > 1 else set() # L is subset of H
        H.difference_update(L)
        S.append((H, L))
        # for each M non-empty subset of L
        for M in chain.from_iterable(combinations(L, k) for k in range(1, len(L)+1)):
            J = I.difference(M)
            if J not in K:
                K.add(J)
                Q.append(J)
    return S

class MPSimMemory(object):
    def __init__(self, n, nb_spaces):
        self.n = n
        self.nb_spaces = nb_spaces
        self.m0 = np.zeros(nb_spaces*n)
        self.make_views()
    def ensure_spaces(self, nb_spaces):
        if self.M0.shape[0] < nb_spaces:
            self.nb_spaces = nb_spaces
            self.m0.resize(nb_spaces*self.n, refcheck=False)
            self.make_views()
    def make_views(self):
        self.M0 = self.m0.reshape(self.nb_spaces, self.n)

def sample_configuration(f, mem, x, S, W):
    """
    sample one configuration reachable from x among the reachable spaces S

    modifies x in-place
    """
    n = len(f)
    # compute apparent rate of transitions
    mem.ensure_spaces(len(S))
    R = mem.M0[:len(S),:]
    R[:,:] = 0. # reset
    # multiplicity of transitions
    # R[i,k] is the multiplicity of a transition modifying k components
    for i, (H, L) in enumerate(S):
        if L:
            # all components of L have to change, multiplicity is 1
            R[i,len(L)-1] = 1
        # multiplicity of H depends on cardinality of subsets
        R[i,len(L):len(L)+len(H)] = binom(len(H), range(1, len(H)+1))
    R *= W # multiply by rate to obtain activity
    R.cumsum(out=mem.m0[:len(S)*n]) # in-place cumsum
    # pick transition
    r = uniform(0, R[-1,-1]) # excludes R[-1,-1]
    # select space s and nb of flips (-1)
    s,m = next(zip(*np.where(R > r)))
    m += 1
    # s = space, m = nb of components to flip
    H, C = S[s]
    if H:
        C.update(choice(list(H),m-len(C), replace=False))
    for i in C:
        x[i] = 1-x[i]

def step(f, mem, x, depth, W):
    S = reachable_spaces(f, x, depth)
    if not S:
        return False
    sample_configuration(f, mem, x, S, W)
    return True

def is_subhypercube(a, b):
    x, H = a
    y, G = b
    return H.issubset(G) and \
            not [i for i in set(x).difference(G) if x[i] != y[i]]

def sample_reachable_attractor(f, mem, x, A, depth, W, refresh_rate=10, emit=None):
    if not isinstance(f, MPBNSim): f = MPBNSim(f)
    I = set(f)
    n = len(f)
    def filter_reachable_attractors(A, x):
        H = spread(f, x, I, n)
        return [(ia,a) for (ia,a) in A if is_subhypercube(a, (x,H))]
    k = 1
    x = x.copy()
    A = filter_reachable_attractors(A, x)
    while len(A) > 1:
        if emit is not None:
            emit(x)
        if not step(f, mem, x, depth, W):
            k = 0
        if k % refresh_rate == 0:
            A = filter_reachable_attractors(A, x)
        k += 1
    return A[0][0]

def sample_trace(f, mem, x, A, depth, W):
    if not isinstance(f, MPBNSim): f = MPBNSim(f)
    I = set(f)
    n = len(f)
    def filter_reachable_attractors(A, x):
        H = spread(f, x, I, n)
        return [(ia,a) for (ia,a) in A if is_subhypercube(a, (x,H))]
    k = 1
    x = x.copy()
    trace = list()
    trace.append(x.copy())
    A = filter_reachable_attractors(A, x)
    while len(A) and x != A[0][1][0]:
        step(f, mem, x, depth, W)
        trace.append(x.copy())
        A = filter_reachable_attractors(A, x)
    return trace


def sample_switchpoint(f, mem, x, A, depth, W):
    """ experimental: sample a trace and stop at an attractor's
    strong bassin, returning the attractor as well."""
    if not isinstance(f, MPBNSim): f = MPBNSim(f)
    I = set(f)
    n = len(f)
    def filter_reachable_attractors(A, x):
        H = spread(f, x, I, n)
        return [(ia,a) for (ia,a) in A if is_subhypercube(a, (x,H))]
    
    names = lambda _A: set(_a_name for _a_name, _a_cfg in _A)
    k = 1
    x = x.copy()
    trace = list()
    A = filter_reachable_attractors(A, x)
    trace.append((x.copy(), names(A)))
    while len(A) > 1:
        step(f, mem, x, depth, W)
        A = filter_reachable_attractors(A, x)
        trace.append((x.copy(), names(A)))
    #return [*trace, [a_name for a_name, a_x in A]] 
    return trace

def convert_attractor(A):
    H = {i for i,v in A.items() if v == '*'}
    x = {i:v for i,v in A.items() if v != '*'}
    return x, H

def estimate_reachable_attractors_probabilities(f, x, A, nb_sims, depth, W):
    f = MPBNSim(f)
    mem = MPSimMemory(len(f), len(f))
    A = list(enumerate(map(convert_attractor, A)))
    C = {ia: 0 for (ia,_) in A}
    for _ in tqdm(range(nb_sims)):
        ia = sample_reachable_attractor(f, mem, x, A, depth, W)
        C[ia] += 1
    for ia, _ in A:
        C[ia] = (C[ia]*100) / nb_sims
    return C

def parallel_estimate_reachable_attractors_probabilities(f, x, A, nb_sims, depth, W,
            nb_jobs=0):

    if nb_jobs == 0:
        nb_jobs = cpu_count()

    f = MPBNSim(f)
    A = list(enumerate(map(convert_attractor, A)))

    q = SimpleQueue()
    r = SimpleQueue()

    def worker(nb_sim):
        seed(int.from_bytes(os.urandom(4)))
        mem = MPSimMemory(len(f), len(f))
        C = {ia: 0 for (ia,_) in A}
        for _ in range(nb_sim):
            ia = sample_reachable_attractor(f, mem, x, A, depth, W)
            C[ia] += 1
            q.put(ia)
        r.put(C)

    # create nb_jobs processes
    w_nb_sims = [nb_sims // nb_jobs] * nb_jobs
    for i in range(nb_sims % nb_jobs):
        w_nb_sims[i] += 1
    procs = [Process(target=worker, args=(n,)) for n in w_nb_sims]

    for p in procs:
        p.start()
    for _ in tqdm(range(nb_sims)):
        q.get()
    for p in procs:
        p.join()

    # combine results
    C = {ia: 0 for (ia,_) in A}
    for _ in range(nb_jobs):
        Cr = r.get()
        for (ia, c) in Cr.items():
            C[ia] += c
    for ia, _ in A:
        C[ia] = (C[ia]*100) / nb_sims
    return C



###
### Parametrizations
###

##
## Depth
##
def constant_maximum_depth(f):
    """
    Returns the dimnesion of `f`
    """
    return len(f)
def constant_unitary_depth(f):
    """
    Returns 1
    """
    return 1
def poly_depth(f, power=1.2):
    n = len(f)
    a = np.arange(1, n+1)
    p = np.arange(n, 0, -1, dtype="float64")**power
    p /= p.sum()
    return lambda: np.random.choice(a, p=p)
def reciprocal_depth(f):
    n = len(f)
    a = np.arange(1, n+1)
    p = 1/np.arange(1, n+1)
    p /= p.sum()
    return lambda: np.random.choice(a, p=p)
def nexponential_depth(f, base=2):
    n = len(f)
    a = np.arange(1, n+1)
    p = 1/ base**np.arange(0, n)
    p /= p.sum()
    return lambda: np.random.choice(a, p=p)




##
## Rates
##
## TODO: resolve this
def uniform_rates(f):
    """
    Returns 1
    """
    return 1
def fully_asynchronous_rates(f):
    """
    Returns an array of length n of the form `1 0 0 .. 0`
    """
    W = np.zeros(len(f))
    W[0] = 1
    return W
def reciprocal_rates(f):
    """
    Returns an array for length n where the i-th component is equal to
    1/i for i ranging from 1 to n
    """
    return 1 / np.arange(1, len(f)+1)
def nexponential_rates(f, base=2):
    """
    Returns an array for length n where the i-th component is equal to
    1/(2**{i-1) for i ranging from 1 to n
    """
    return 1 / base**np.arange(0, len(f))
