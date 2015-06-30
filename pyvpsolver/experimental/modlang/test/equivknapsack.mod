$PARAM[m]{len(a)};

set I := 1..m;
var pi{{0} union I} >= 0;
var theta{V} >= 0;

$PY{
m = len(a)
W = [a0]+[1]*len(a)
w = [[a[i]]+[1 if j == i else 0 for j in xrange(m)] for i in xrange(m)]
b = [1 if w[i] <= W else 0 for i in xrange(m)]
labels = [i+1 for i in xrange(m)]
};

$GRAPH[V,A]{W, w, labels, b};

minimize obj: pi[0];
s.t. gamma{(u,v,i) in A}: theta[v] >= theta[u]+(if i != 'LOSS' then pi[i] else 0);
s.t. pi0: pi[0] = theta['T'];
s.t. pisum: sum{i in I} pi[i] = 1+2*pi[0];

solve;

display{i in I} pi[i];
display pi[0];
display theta['T'];
