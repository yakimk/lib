import math

def f_stars_and_bars(R, k):
    # number of ways to distribute R identical items into k labeled boxes
    if R < 0:
        return 0
    if k <= 0:
        return 0 if R != 0 else 1
    return math.comb(R + k - 1, k - 1)

def g_count_T_M_r(T_max, M, r):
    if r == 0:
       return [0] * (T_max + 1)

    dp0 = [0] * (T_max + 1)  # no M seen
    dp1 = [0] * (T_max + 1)  # some M seen
    dp0[0] = 1

    for _ in range(r):
        # difference arrays length T_max+2 to support R+1 index
        diff0 = [0] * (T_max + 2)
        diff1 = [0] * (T_max + 2)

        def range_add(diff, L, R, val):
            if L > R or L > T_max:
                return
            if R > T_max:
                R = T_max
            diff[L] += val
            diff[R + 1] -= val

        for s in range(T_max + 1):
            v0 = dp0[s]
            v1 = dp1[s]
            if v0 == 0 and v1 == 0:
                continue
            # allowed c: 0..min(M, T_max - s)
            maxc = min(M, T_max - s)
            low = s
            high = s + maxc
            if low <= high:
                if v0:
                    # add v0 to newdp0[low..high]
                    range_add(diff0, low, high, v0)
                    # if M in allowed c-range, move single index s+M from newdp0 to newdp1
                    if maxc >= M: # means s + M <= T_max
                        idx = s + M
                        range_add(diff0, idx, idx, -v0)
                        range_add(diff1, idx, idx, v0)
                if v1:
                    # add v1 to newdp1[low..high]
                    range_add(diff1, low, high, v1)

        new0 = [0] * (T_max + 1)
        new1 = [0] * (T_max + 1)
        cur = 0
        for i in range(T_max + 1):
            cur += diff0[i]
            new0[i] = cur
        cur = 0
        for i in range(T_max + 1):
            cur += diff1[i]
            new1[i] = cur

        dp0, dp1 = new0, new1

    return dp1  # g(T) = dp1[T] for T=0..T_max


def count_by_M_T(n, N, K_set):
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

    for M in range(0, M_max + 1):
        T_min = M
        T_max_possible = min(r * M, N - k * (M + 1))
        if T_max_possible < T_min:
            continue

        g = g_count_T_M_r(T_max_possible, M, r)

        for T in range(T_min, T_max_possible + 1):
            R = N - k * (M + 1) - T
            if R < 0:
                continue
            f = f_stars_and_bars(R, k)
            val = f * g[T]
            total += val

    return total

def brute_g(r, M, T_max):
    from itertools import product
    g = [0]*(T_max+1)
    for tup in product(range(M+1), repeat=r):
        s = sum(tup)
        if s <= T_max and any(x == M for x in tup):
            g[s] += 1
    return g


# n = 40
# K_set = {0,1}   # k = 2
# N = 100
# print(count_by_M_T(n, N, K_set))

 # print(3, 2, 7, brute_g(3, 2, 7))
# # print(4, 3, 14, brute_g(4, 3, 14))
# # print(6, 4, 30, brute_g(6, 4, 30))
