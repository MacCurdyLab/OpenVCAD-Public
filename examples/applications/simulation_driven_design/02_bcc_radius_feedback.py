"""Run the complete solid-envelope to BCC-radius feedback study."""

import argparse
import json

from bcc_study import run_study


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--fast",
    action="store_true",
    help="Reduce TET4, lattice-volume, and render cost without changing the workflow.",
)
parser.add_argument(
    "--no-render",
    action="store_true",
    help="Skip headless images for solver-only validation.",
)
arguments = parser.parse_args()

output_name = "study2_bcc_fast" if arguments.fast else "study2_bcc"
study_metrics = run_study(
    fast=arguments.fast,
    render=not arguments.no_render,
    output_name=output_name,
)
print(json.dumps(study_metrics, indent=2, sort_keys=True))
