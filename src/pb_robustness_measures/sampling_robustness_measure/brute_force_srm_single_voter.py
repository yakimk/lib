# enumerate all integer vectors c0..c3 >=0 summing to 10
def gen_compositions(nvars, total):
    if nvars == 1:
        yield (total,)
    else:
        for i in range(total+1):
            for tail in gen_compositions(nvars-1, total-i):
                yield (i,)+tail

n = 4
K = {0,1}
N = 10
by_M = {}
for vec in gen_compositions(n, N):
    nonK = [vec[j] for j in range(n) if j not in K]
    Kvals = [vec[i] for i in K]
    if min(Kvals) > max(nonK):
        M = max(nonK) if nonK else -1
        by_M.setdefault(M, []).append(vec)

for M in sorted(by_M):
    print("M=", M, "count=", len(by_M[M]), "examples:", by_M[M])
print("TOTAL =", sum(len(v) for v in by_M.values()))
