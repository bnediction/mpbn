% f1(x) = !x2
node(1).
clause(1,0,2,-1).
% f2(x) = !x1
node(2).
clause(2,0,1,-1).
% f3(x) = !x1 & x2
node(3).
clause(3,0,1,-1). clause(3,0,2,1).
