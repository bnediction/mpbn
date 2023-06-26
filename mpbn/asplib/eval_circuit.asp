mp_eval(E,T,N,V) :- timepoint(E,T), node(N), circuit(N,root,C), evalcircuit(E,T,N,C,V).
mp_eval(E,T,N,V) :- timepoint(E,T), node(N), constant(N,V).

%
% leafs
%
evalcircuit(E,T,N,(var,M),V) :- circuit(N,(var,M)), mp_reach(E,T,M,V).
evalcircuit(E,T,N,(constant,V),V) :- timepoint(E,T),node(N),circuit((constant,V)).

%
% operators
%

% negation
evalcircuit(E,T,N,C,-V) :- circuit(N,C,neg), circuitedge(N,C,D),
                            evalcircuit(E,T,N,D,V).

% disjunction
evalcircuit(E,T,N,C,1) :- circuit(N,C,or), circuitedge(N,C,D),
                            evalcircuit(E,T,N,D,1).
evalcircuit(E,T,N,C,-1) :- timepoint(E,T), circuit(N,C,or);
                            evalcircuit(E,T,N,D,-1): circuitedge(N,C,D).

% conjunction
evalcircuit(E,T,N,C,-1) :- circuit(N,C,and), circuitedge(N,C,D),
                            evalcircuit(E,T,N,D,-1).
evalcircuit(E,T,N,C,1) :- timepoint(E,T), circuit(N,C,and);
                            evalcircuit(E,T,N,D,1): circuitedge(N,C,D).
