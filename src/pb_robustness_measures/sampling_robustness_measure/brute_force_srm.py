from itertools import combinations_with_replacement, product

def gen_compositions(nvars, total):
    if nvars == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in gen_compositions(nvars - 1, total - first):
            yield (first,) + tail

def enum_supporter_multisets_for_vector(c_vec, s_list):
    n = len(s_list)
    lists = []
    for i in range(n):
        c = c_vec[i]
        s = s_list[i]
        if c > 0 and s == 0:
            return
        lists.append(list(combinations_with_replacement(range(s), c)))
    for prod_choice in product(*lists):
        yield prod_choice

def brute_force_list_valid_assignments(s_list, N, K_set, max_print=200):
    n = len(s_list)
    k = len(K_set)
    r = n - k
    total_count = 0
    printed = 0
    examples = []

    for c_vec in gen_compositions(n, N):
        nonK_vals = [c_vec[i] for i in range(n) if i not in K_set]
        K_vals = [c_vec[i] for i in K_set]
        if len(nonK_vals) == 0:
            continue
        if min(K_vals) <= max(nonK_vals):
            continue  # not a strct ineq
        local_count = 0
        for sup_choice in enum_supporter_multisets_for_vector(c_vec, s_list):
            total_count += 1
            local_count += 1
            if printed < max_print:
                examples.append((c_vec, sup_choice))
                printed += 1
        if local_count > 0:
            print(f"project-counts {c_vec} -> {local_count} supporter-level assignments")
    print("--- done enumeration ---")
    print(f"Total supporter-level assignments found: {total_count}")
    return total_count, examples

if __name__ == "__main__":
    s_list = [2, 1, 2, 1]
    n = len(s_list)
    K_set = {0, 1}
    N = 6

    total, examples = brute_force_list_valid_assignments(s_list, N, K_set, max_print=50)
    for idx, (c_vec, sup_choice) in enumerate(examples):
        print(idx+1, "counts=", c_vec, "supporters=", sup_choice)
