"""Run the complete Agilus30/Vero cantilever feedback study."""

import argparse
import json

from cantilever_study import run_study


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--fast",
    action="store_true",
    help="Reduce TET4 and render resolution while retaining the full workflow.",
)
parser.add_argument(
    "--no-render",
    action="store_true",
    help="Skip headless images for solver-only validation.",
)
arguments = parser.parse_args()

output_name = "study1_cantilever_fast" if arguments.fast else "study1_cantilever"
study_metrics = run_study(
    fast=arguments.fast,
    render=not arguments.no_render,
    output_name=output_name,
)
print(json.dumps(study_metrics, indent=2, sort_keys=True))
