
mp_eval(E,T,N,clause,C,1) :- mp_reach(E,T,L,V) : clause(N,C,L,V);
                                timepoint(E,T), clause(N,C,_,_).
mp_eval(E,T,N,clause,C,-1) :- mp_reach(E,T,L,-V), clause(N,C,L,V).
mp_eval(E,T,N,V) :- timepoint(E,T), node(N), constant(N,V).
mp_eval(E,T,N,1) :- mp_eval(E,T,N,clause,C,1), clause(N,C,_,_).
mp_eval(E,T,N,-1) :- mp_eval(E,T,N,clause,C,-1) : clause(N,C,_,_);
                            node(N), timepoint(E,T), clause(N,_,_,_).

