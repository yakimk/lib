from fractions import Fraction
from math import comb
from pb_robustness_measures.rules.greedyAV import greedy_av

def compute_ways_for_project(s, max_c):
    ways = [0] * (max_c + 1)
    ways[0] = 1
    for _ in range(s):
        pref = [0] * (max_c + 1)
        running = 0
        for t in range(max_c + 1):
            running += ways[t]
            pref[t] = running
        ways = pref
    return ways

def convolve_truncate(a, b, maxdeg):
    n = maxdeg + 1
    c = [0] * n
    nz_a = [i for i,v in enumerate(a) if v != 0]
    nz_b = [i for i,v in enumerate(b) if v != 0]
    for i in nz_a:
        ai = a[i]
        for j in nz_b:
            t = i + j
            if t > maxdeg:
                break
            c[t] += ai * b[j]
    return c

def count_with_supporters(n, s_list, m, K_set):
    k = len(K_set)
    if k == 0:
        return 0
    if k == n:
        return 0

    ways = [compute_ways_for_project(s, m) for s in s_list]

    total = 0
    r = n - k
    M_max = m // k - 1
    if M_max < 0:
        return 0

    for M in range(M_max + 1):
        T_min = M
        T_max = min(r * M, m - k * (M + 1))
        if T_max < T_min:
            continue

        poly_non_M = [1] + [0] * T_max
        poly_non_Mminus = [1] + [0] * T_max
        for j in range(n):
            if j in K_set:
                continue
            Tj_M = [ways[j][c] if c <= M else 0 for c in range(T_max + 1)]
            poly_non_M = convolve_truncate(poly_non_M, Tj_M, T_max)
            if M == 0:
                Tj_Mm1 = [0] * (T_max + 1)
            else:
                Tj_Mm1 = [ways[j][c] if c <= M-1 else 0 for c in range(T_max + 1)]
            poly_non_Mminus = convolve_truncate(poly_non_Mminus, Tj_Mm1, T_max)

        poly_diff = [poly_non_M[t] - poly_non_Mminus[t] for t in range(T_max + 1)]
        polyK = [1] + [0] * m
        for i in range(n):
            if i not in K_set:
                continue
            Ri = [ways[i][c] if c >= M+1 else 0 for c in range(m + 1)]
            polyK = convolve_truncate(polyK, Ri, m)

        for T in range(T_min, T_max + 1):
            S = m - T
            total += polyK[S] * poly_diff[T]

    return total


def plurality_sampling_robustness_measure(
    instance,
    profile,
    target=None,
    samples: int = 100,
):
    projects = list(instance)
    idx = {p: i for i, p in enumerate(projects)}

    if target is None:
        allocation = greedy_av(instance, profile)
        winners = set(allocation)
        K_set = {idx[p] for p in winners if p in idx}
    else:
        if target not in idx:
            raise ValueError("target project not in instance")
        K_set = {idx[target]}

    s_list = [int(profile.approval_score(p)) for p in projects]
    # print("Sum of S list", sum(s_list), len(s_list), s_list)
    # print("Kset", len(K_set), K_set)

    m = int(samples)
    if m < 0:
        raise ValueError("Number of samples  must be non-negative")

    S = sum(s_list)
    if S == 0:
        # edge case
        return Fraction(0, 1)

    total_unordered_multisets = comb(S + m - 1, m)

    count_valid_multisets = count_with_supporters(len(s_list), s_list, m, K_set)

    return Fraction(count_valid_multisets, total_unordered_multisets)

