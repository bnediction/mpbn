mp_eval(E,T,N,V) :- timepoint(E,T), node(N), constant(N,V).

mp_eval(E,T,N,clause,C,1) :- mp_reach(E,T,L,V) : clause(N,C,L,V);
                                timepoint(E,T), clause(N,C,_,_).
mp_eval(E,T,N,clause,C,-1) :- mp_reach(E,T,L,-V), clause(N,C,L,V).
mp_eval(E,T,N,1) :- mp_eval(E,T,N,clause,C,1), clause(N,C,_,_).
mp_eval(E,T,N,-1) :- mp_eval(E,T,N,clause,C,-1) : clause(N,C,_,_);
                            node(N), timepoint(E,T), clause(N,_,_,_); unate(N).

mp_eval(E,T,N,V) :- evalbdd(E,T,N,V), node(N), timepoint(E,T), V=-1.
evalbdd(E,T,V,V) :- mp_reach(E,T,_,_), V=-1.
evalbdd(E,T,B,V) :- bdd(B,N,_,HI), mp_reach(E,T,N,1), evalbdd(E,T,HI,V).
evalbdd(E,T,B,V) :- bdd(B,N,LO,_), mp_reach(E,T,N,-1), evalbdd(E,T,LO,V).
evalbdd(E,T,B,V) :- mp_reach(E,T,_,_), bdd(B,V), V=-1.
