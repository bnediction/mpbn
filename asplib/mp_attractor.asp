#include "mp_eval.asp".
timepoint(__a,0).
1 { mp_reach(__a,0,N,-1);mp_reach(__a,0,N,1) } :- node(N).
mp_reach(__a,0,N,V) :- mp_eval(__a,0,N,V).

attractor(N,V) :- mp_reach(__a,0,N,V).
#show attractor/2.
