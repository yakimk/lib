import math
from itertools import product

def ways_list(s, max_c):
    if max_c < 0:
        return []
    ways = [0] * (max_c + 1)
    ways[0] = 1
    for c in range(1, max_c + 1):
        ways[c] = ways[c - 1] * (s + c - 1) // c
    return ways


def g_count_T_M_r_weighted(T_max, M, losers_s_list):

    r = len(losers_s_list)
    if r == 0:
        return [0] * (T_max + 1)

    ways_per_loser = [ways_list(s, min(M, T_max)) for s in losers_s_list]

    dp0 = [0] * (T_max + 1)  # no M seen
    dp1 = [0] * (T_max + 1)  # some M seen
    dp0[0] = 1

    for j in range(r):
        w = ways_per_loser[j] 
        new0 = [0] * (T_max + 1)
        new1 = [0] * (T_max + 1)
        for s in range(T_max + 1):
            v0 = dp0[s]
            v1 = dp1[s]
            if v0:
                maxc = min(M, T_max - s)
                for c in range(maxc + 1):
                    if c < M:
                        new0[s + c] += v0 * w[c]
                    else:  # c == M
                        new1[s + c] += v0 * w[c]
            if v1:
                maxc = min(M, T_max - s)
                for c in range(maxc + 1):
                    new1[s + c] += v1 * w[c]
        dp0, dp1 = new0, new1

    return dp1


def f_count_R_k_naive(R_max, winners_s_list, M, m):
    k = len(winners_s_list)
    if k == 0:
        res = [0] * (R_max + 1)
        if R_max >= 0:
            res[0] = 1
        return res

    ways_full_per_winner = [ways_list(s, m) for s in winners_s_list]
    dp = [0] * (R_max + 1)
    dp[0] = 1
    for j in range(k):
        wfull = ways_full_per_winner[j]
        new = [0] * (R_max + 1)
        for s in range(R_max + 1):
            v = dp[s]
            if v == 0:
                continue
            maxc = R_max - s
            for c in range(maxc + 1):
                idx = M + 1 + c
                if idx <= m:
                    weight = wfull[idx]
                else:
                    weight = 0
                new[s + c] += v * weight
        dp = new
    return dp 


def count_by_M_T_multi(n, N, s_list, K_set):

    k = len(K_set)
    if k == 0:
        return 0
    if k == n:
        return 0

    r = n - k
    total = 0

    M_max = (N // k) - 1
    if M_max < 0:
        return 0

    losers = [j for j in range(n) if j not in K_set]
    winners = [i for i in range(n) if i in K_set]

    for M in range(0, M_max + 1):
        T_min = M
        T_max_possible = min(r * M, N - k * (M + 1))
        if T_max_possible < T_min:
            continue

        losers_s = [s_list[j] for j in losers]
        g = g_count_T_M_r_weighted(T_max_possible, M, losers_s)

        R_high = N - k * (M + 1) - T_min
        if R_high < 0:
            continue
        winners_s = [s_list[i] for i in winners]
        f = f_count_R_k_naive(R_high, winners_s, M, N) 

        for T in range(T_min, T_max_possible + 1):
            R = N - k * (M + 1) - T
            if 0 <= R <= R_high:
                total += f[R] * g[T]

    return total

def brute_count(n, s_list, N, K_set):
    total = 0
    for tup in product(range(N + 1), repeat=n):
        if sum(tup) != N:
            continue
        if not K_set:
            continue
        min_win = min(tup[i] for i in K_set)
        max_lose = max(tup[j] for j in range(n) if j not in K_set)
        if min_win <= max_lose:
            continue
        mult = 1
        for i, xi in enumerate(tup):
            if xi > 0 and s_list[i] == 0:
                mult = 0
                break
            mult *= math.comb(s_list[i] + xi - 1, xi) if xi > 0 else 1
        total += mult
    return total


if __name__ == "__main__":
    n = 4
    s_list = [2, 1, 2, 1]
    K_set = {0, 1}
    N = 6
    print("count_by_M_T_multi:", count_by_M_T_multi(n, N, s_list, K_set))
    print("brute_count:", brute_count(n, s_list, N, K_set))