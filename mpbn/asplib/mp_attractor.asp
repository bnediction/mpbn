
timepoint(__a,final).
1 { mp_reach(__a,final,N,-1);mp_reach(__a,final,N,1) } :- node(N).
mp_reach(__a,final,N,V) :- mp_eval(__a,final,N,V).

attractor(N,V) :- mp_reach(__a,final,N,V).
