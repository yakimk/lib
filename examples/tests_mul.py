import os
import csv
import matplotlib.pyplot as plt
from pabutools import election
from pb_robustness_measures.sampling_robustness_measure.srm import plurality_sampling_robustness_measure

PB_FOLDER = "ex"
MULTIPLIERS = [0.1]

def compute_srm_for_instance(pb_file, multipliers):
    instance, profile = election.parse_pabulib(pb_file)
    projects = list(instance)
    s_list = [int(profile.approval_score(p)) for p in projects]
    S_original = sum(s_list)
    results = []
    for mult in multipliers:
        print("Multiplicity: ", mult)
        m = max(1, int(round(mult * S_original)))
        res = plurality_sampling_robustness_measure(instance, profile, target=None, samples=m)
        if isinstance(res, tuple):
            frac = res[0]
        else:
            frac = res
        try:
            value = float(frac)
        except Exception:
            value = float("nan")
        results.append((mult, m, value))
    return results

def main():
    pb_files = sorted(f for f in os.listdir(PB_FOLDER) if f.endswith(".pb"))
    if not pb_files:
        print(f"No .pb files found inside '{PB_FOLDER}'")
        return

    srm_results = {}
    for fname in pb_files:
        full_path = os.path.join(PB_FOLDER, fname)
        srm_results[fname] = compute_srm_for_instance(full_path, MULTIPLIERS)

    plt.figure(figsize=(10, 6))
    for fname, triplets in srm_results.items():
        xs = [mult for (mult, _, _) in triplets]
        ys = [val for (_, _, val) in triplets]
        plt.plot(xs, ys, marker="o", label=fname)

    plt.xlabel("Multiplier")
    plt.ylabel("SRM probability")
    plt.title("Plurality Sampling Robustness Measure - multiplicative samples")
    plt.grid(True)
    plt.legend()

    out_png = "srm_multipliers_plot.png"
    plt.savefig(out_png, dpi=200)

    out_csv = "srm_multipliers_data.csv"
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["instance", "multiplier", "samples_m", "srm_prob"])
        for fname, triplets in srm_results.items():
            for mult, m, val in triplets:
                writer.writerow([fname, mult, m, val])

    print(f"Saved plot → {out_png}")
    print(f"Saved CSV → {out_csv}")

if __name__ == "__main__":
    main()





