
mp_reach(E,T1,N,V) :- is_reachable(E,T1,T2), mp_state(E,T1,N,V).

mp_ext(E,T1,N,V) :- mp_eval(E,T1,N,V), is_reachable(E,T1,T2), mp_state(E,T2,N,V).
{mp_ext(E,T1,N,V)} :- mp_eval(E,T1,N,V), is_reachable(E,T1,T2), not mp_state(E,T2,N,V), mp_state(E,T2,N,-V).

mp_reach(E,T,N,V) :- mp_ext(E,T,N,V).

:- is_reachable(E,T1,T2), mp_state(E,T2,N,V), not mp_reach(E,T1,N,V).
:- is_reachable(E,T1,T2), mp_state(E,T2,N,V), mp_ext(E,T,N,-V), not mp_ext(E,T,N,V).
