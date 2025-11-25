import os
import csv
import matplotlib.pyplot as plt
from pabutools import election

from pb_robustness_measures.sampling_robustness_measure.srm import (
    plurality_sampling_robustness_measure,
)

PB_FOLDER = "small_examples"

SAMPLE_SIZES = [10, 50, 100, 200, 300, 400, 1000]

def compute_srm_for_instance(pb_file):
    print(f"\n=== Loading instance: {pb_file} ===")
    instance, profile = election.parse_pabulib(pb_file)

    results = []

    for m in SAMPLE_SIZES:
        print(f"  Computing SRM(m={m}) ...")
        res = plurality_sampling_robustness_measure(
            instance,
            profile,
            target=None,
            samples=m,
        )

        if isinstance(res, tuple):
            frac = res[0]
        else:
            frac = res

        try:
            value = float(frac)
        except Exception:
            value = float("nan")

        print(f"     → {value}")
        results.append(value)

    return results


def main():

    pb_files = sorted(
        f for f in os.listdir(PB_FOLDER) if f.endswith(".pb")
    )

    if not pb_files:
        print(f"No .pb files found inside '{PB_FOLDER}'")
        return

    print("Found PB files:")
    for f in pb_files:
        print("  -", f)

    #  {filename: [values]}
    srm_results = {}

    for fname in pb_files:
        full_path = os.path.join(PB_FOLDER, fname)
        srm_results[fname] = compute_srm_for_instance(full_path)


    plt.figure(figsize=(10, 6))

    for fname, vals in srm_results.items():
        plt.plot(SAMPLE_SIZES, vals, marker="o", label=fname)

    plt.xlabel("Number of samples (m)")
    plt.ylabel("SRM probability")
    plt.title("Plurality Sampling Robustness Measure – All small_examples")
    plt.grid(True)
    plt.legend()

    out_png = "srm_plot.png"
    plt.savefig(out_png, dpi=200)
    print(f"\nSaved plot → {out_png}")

    out_csv = "srm_data.csv"
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["instance"] + SAMPLE_SIZES
        writer.writerow(header)

        for fname, vals in srm_results.items():
            writer.writerow([fname] + vals)

    print(f"Saved CSV → {out_csv}")


if __name__ == "__main__":
    main()
