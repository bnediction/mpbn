import json
import mpbn
import sys
from argparse import ArgumentParser

import mpbn.simulation as mpbn_sim

def main():
    cmdline = ArgumentParser()
    cmdline.add_argument("--profile", action="store_true", default=False,
                            help="Perform code profiling")
    cmdline.add_argument("--save-in", type=str, dest="save",
                            help="Save simulation results within given diretory")
    cmdline.add_argument("--repeat", type=int, default=1,
                            help="Repeat simulations")
    cmdline.add_argument("--nb-jobs", type=int, default=1,
                            help="Parallelize simulations with number of jobs (0 for all available CPUs)")
    cmdline.add_argument("json_file",
                            help="Simulation setup")
    args = cmdline.parse_args()


    with open(args.json_file) as fp:
        setup = json.load(fp)
    json.dump(setup, sys.stdout, indent=2)
    print()

    if "bnet_file" in setup:
        f = mpbn.load(setup["bnet_file"])
    elif "f" in setup:
        f = mpbn.MPBooleanNetwork(setup["f"])

    if args.save:
        result = {"setup": setup,
                "results": []}

    x0 = f.zero()
    for i in setup.get("init_active", ()):
        x0[i] = 1


    if "label_attractor" in setup:
        conditions = [(eval(s[0]), s[1]) for s in setup["label_attractor"][:-1]]
        default_label = setup["label_attractor"][-1]
        def label_attractor(a):
            for cond, label in conditions:
                if cond(a):
                    return label
            return default_label
    else:
        label_attractor = None


    def str_attractor(a):
        active = ', '.join([n for n, v in a.items() if v == 1])
        if active:
            active = f"[{active}]=1 "
        star = ', '.join([n for n, v in a.items() if v == '*'])
        if star:
            star = f"[{star}]=*"
        if label_attractor is not None:
            label = f" ({label_attractor(a)})"
        else:
            label = ""
        return f"{active}{star}{label}"

    print()
    print("Reachable attractors:")
    A = list(f.attractors(reachable_from=x0))
    for i, a in enumerate(A):
        print(f"{i}. {str_attractor(a)}")


    if "mutants" in setup:
        def patch_model(f, patch):
            f = mpbn.MPBooleanNetwork(f)
            for i, fi in patch.items():
                f[i] = fi
            return f
        f_mutants = {name: patch_model(f, patch) for name, patch in
                        setup["mutants"].items()}
        for f_muted in f_mutants.values():
            for a in f_muted.attractors(reachable_from=x0):
                if a not in A:
                    print(f"{len(A)}. {str_attractor(a)}")
                    A.append(a)

    print()

    if label_attractor:
        AL = list(map(label_attractor, A))
        labels = list(sorted(list(set(AL))))
        zero = {label: 0 for label in labels}


    def handle_result(exp, a_p):
        if label_attractor:
            l_p = zero.copy()
            for a, p in a_p.items():
                l_p[AL[a]] += p
            a_p = l_p
        if args.save:
            result["results"].append({"experiment": exp, "probabilities": a_p})
        print(a_p)

    nb_sims = setup["nb_sims"]

    def do_experiments(f, A):
        for exp in setup["experiments"]:
            if "name" not in exp:
                continue
            for _ in range(args.repeat):
                rates = getattr(mpbn_sim, f"{exp['rates']}_rates")
                depth = getattr(mpbn_sim, f"{exp['depth']}_depth")
                rates_args = exp.get("rate_args", {})
                depth_args = exp.get("depth_args", {})
                print(f"- {depth.__name__}{depth_args}\t{rates.__name__}{rates_args}")
                def do():
                    margs = (f, x0, A, nb_sims,
                                depth(f, **depth_args),
                                rates(f, **rates_args))
                    kwargs = {}
                    meth = mpbn_sim.estimate_reachable_attractors_probabilities
                    if args.nb_jobs != 1:
                        meth = mpbn_sim.parallel_estimate_reachable_attractors_probabilities
                        kwargs["nb_jobs"] = args.nb_jobs
                    res = meth(*margs, **kwargs)
                    handle_result(exp, res)

                if args.profile:
                    import cProfile
                    with cProfile.Profile() as pr:
                        do()
                    pr.print_stats(sort="time")
                else:
                    do()
                print()

    if "mutants" in setup:
        def print_name(name):
            print("###")
            print(f"### {name}")
            print("###")
            print()
        if args.save:
            result["mutant_results"] = {}
            def commit_result(name):
                result["mutant_results"][name] = result["results"].copy()
                result["results"].clear()
        for name, f_mut in [("Wild type", f)] + list(f_mutants.items()):
            print_name(name)
            B = list(f_mut.attractors(reachable_from=x0))
            def ensure_attractor(a):
                if a in B:
                    return a
                return {"__masked__": '*'}
            myA = [ensure_attractor(a) for a in A]
            do_experiments(f_mut, myA)
            if args.save:
                commit_result(name)
        if args.save:
            result["results"] = result["mutant_results"]
            del result["mutant_results"]
    else:
        do_experiments(f, A)

    if args.save:
        import os
        import datetime
        now = datetime.datetime.now()
        if not os.path.isdir("results"):
            os.mkdir("results")
        basename = os.path.basename(args.json_file).split(".")[0]
        timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        output_name = os.path.join("results", f"{basename}_{timestamp}_{os.getpid()}.json")
        with open(output_name, "w") as fp:
            json.dump(result, fp, indent=3)
