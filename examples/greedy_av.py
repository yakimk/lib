#!/usr/bin/env python3

import sys
import os
import argparse
import logging
from glob import glob

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "src")))

from pabutools.visualisation.visualisation import MESVisualiser
from pabutools.rules.mes import method_of_equal_shares
from pabutools.rules.phragmen import sequential_phragmen
from pabutools import election
from pabutools.election import Cost_Sat
from pb_robustness_measures.visualization.av_graph import av_graph
from pb_robustness_measures.sampling_robustness_measure.srm import plurality_sampling_robustness_measure
from pb_robustness_measures.rules.greedyAV import greedy_av

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def read_example_file(filepath):
    """
    Expected (non-empty, non-comment) lines:
        1: path to .pb
        2: name
        3: voters (int)
        4: projects (int)
        5: budget (int or float)
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]

    if len(lines) < 5:
        raise ValueError(
            f"Example file '{filepath}' must contain at least 5 non-comment lines: "
            "(path, name, voters, projects, budget)."
        )

    pb_path = lines[0]
    name = lines[1]
    voters = int(lines[2])
    projects = int(lines[3])
    budget = float(lines[4])  # supports integer or decimal budgets

    # resolve relative paths relative to the example file
    if not os.path.isabs(pb_path):
        pb_path = os.path.normpath(os.path.join(os.path.dirname(filepath), pb_path))

    return pb_path, name, voters, projects, budget


def process_example(pb_path, name, voters, projects, budget, show_labels=False):
    logging.info(
        f"Processing: {name} (voters={voters}, projects={projects}, budget={budget})"
    )

    if not os.path.exists(pb_path):
        raise FileNotFoundError(f"PB file not found: {pb_path}")

    instance, profile = election.parse_pabulib(pb_path)

    # Now pass voters/projects/budget to av_graph
    av_graph(
        instance,
        profile,
        name=name,
        show_labels=show_labels,
        voters=voters,
        projects=projects,
        budget=budget,
    )

    logging.info(f"Finished: {name}")


def collect_example_files(paths_or_dirs):
    files = []
    for p in paths_or_dirs:
        if os.path.isdir(p):
            for f in sorted(glob(os.path.join(p, "*"))):
                if os.path.isfile(f):
                    files.append(f)
        elif os.path.isfile(p):
            files.append(p)
        else:
            logging.warning(f"Path does not exist (ignored): {p}")
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run av_graph with example files (path, name, voters, projects, budget)."
    )
    parser.add_argument("paths", nargs="*", help="Example files or directories.")
    parser.add_argument("--dir", "-d", help="Directory containing example files.")
    parser.add_argument("--show-labels", action="store_true")
    args = parser.parse_args(argv)

    input_paths = list(args.paths)
    if args.dir:
        input_paths.append(args.dir)

    if not input_paths:
        parser.error("Provide example files or a directory with --dir.")

    example_files = collect_example_files(input_paths)
    if not example_files:
        logging.error("No example files found.")
        return 2

    for ex_file in example_files:
        try:
            pb_path, name, voters, projects, budget = read_example_file(ex_file)
            process_example(pb_path, name, voters, projects, budget, show_labels=args.show_labels)
        except Exception as e:
            logging.exception(f"Error processing '{ex_file}': {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
