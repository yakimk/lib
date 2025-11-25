import argparse
import os
import sys
import csv
from math import isfinite

# sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "src")))

from pabutools import election
from pb_robustness_measures.sampling_robustness_measure.srm import plurality_sampling_robustness_measure
from pb_robustness_measures.rules.greedyAV import greedy_av

import matplotlib.pyplot as plt
import numpy as np
from fractions import Fraction
from typing import List

def load_instance(path: str):
    print(f"Loading {path} ...")
    instance, profile = election.parse_pabulib(path)
    return instance, profile

def run_on_files(pb_paths: List[str], multipliers: List[float], out_png: str, out_csv: str, mc_samples: int, verbose: bool):
    series = []
    for path in pb_paths:
        if not os.path.exists(path):
            print(f"Warning: {path} not found — skipping.")
            continue

        instance, profile = load_instance(path)
        projects = list(instance)
        s_list = [int(profile.approval_score(p)) for p in projects]
        S_original = sum(s_list)
        if S_original == 0:
            print(f"Instance {path} has zero approvals; skipping.")
            continue

        m_values = [max(1, int(round(mult * S_original))) for mult in multipliers]
        probs = []
        raw_info = []
        for m in m_values:
            if verbose:
                print(f"  computing SRM for m={m} (samples = {m}, S_original={S_original}) ...")
            res = plurality_sampling_robustness_measure(
                instance, profile,
                target=None,
                samples=m,
            )
            frac = res if isinstance(res, Fraction) else res
            if isinstance(frac, tuple) and len(frac) >= 1:
                frac_val = frac[0]
            else:
                frac_val = frac
            try:
                prob_float = float(frac_val) if frac_val is not None else float("nan")
            except Exception:
                prob_float = float("nan")

            probs.append(prob_float)
            raw_info.append((m, frac_val))
            if verbose:
                print(f"    -> SRM = {prob_float}")

        series.append({
            "label": os.path.basename(path),
            "S_original": S_original,
            "multipliers": multipliers,
            "m_values": m_values,
            "probs": probs,
            "raw_info": raw_info
        })

    plt.figure(figsize=(10,6))
    for s in series:
        xs = [m / s["S_original"] for m in s["m_values"]]
        ys = s["probs"]
        plt.plot(xs, ys, marker='o', label=f'{s["label"]} (S={s["S_original"]})')
    plt.xlabel("samples / original_votes (ratio)")
    plt.ylabel("SRM probability")
    plt.title("Plurality-sampling robustness measure")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    print(f"Saved combined plot to {out_png}")
    with open(out_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["instance", "S_original", "multiplier", "m", "srm_prob"])
        for s in series:
            for mult, m, prob in zip(s["multipliers"], s["m_values"], s["probs"]):
                writer.writerow([s["label"], s["S_original"], mult, m, prob])
    print(f"Saved numeric results to {out_csv}")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--pb", nargs="+", required=False,
                   default=[
                       "netherlands_amsterdam_252_.pb",
                       "poland_warszawa_2020_ursynow.pb",
                       "poland_warszawa_2024_.pb",
                   ],
                   help="Paths to .pb files (up to 3).")
    p.add_argument("--multipliers", nargs="+", type=float, default=[0.2, 0.5, 1.0, 1.2, 2.0],
                   help="Sample-size multipliers relative to original votes")
    p.add_argument("--out", default="srm_combined.png", help="Output plot PNG")
    p.add_argument("--csv", default="srm_results.csv", help="Output CSV of numeric results")
    p.add_argument("--mc", type=int, default=20000, help="MC samples if SRM falls back to Monte-Carlo")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    return p.parse_args()

if __name__ == "__main__":
    import argparse
    args = parse_args()
    pb_paths = args.pb[:3]
    run_on_files(pb_paths, args.multipliers, args.out, args.csv, args.mc, args.verbose)
