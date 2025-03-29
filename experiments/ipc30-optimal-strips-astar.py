#! /usr/bin/env python

import platform
import re
import os

from pathlib import Path

from downward import suites
from downward.reports.absolute import AbsoluteReport
from lab.environments import TetralithEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute, geometric_mean
from astar_parser import AStarParser
import utils

# Create custom report class with suitable info and error attributes.
class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]

DIR = Path(__file__).resolve().parent
REPO = DIR.parent
BENCHMARKS_DIR = os.environ["BENCHMARKS_PDDL_DOWNWARD"]

NODE = platform.node()
REMOTE = re.match(r"tetralith\d+.nsc.liu.se|n\d+", NODE)
if REMOTE:
    ENV = TetralithEnvironment(
        setup=TetralithEnvironment.DEFAULT_SETUP,
        memory_per_cpu="8G",
        extra_options="#SBATCH --account=naiss2024-5-421")
    SUITE = utils.SUITE_OPTIMAL_STRIPS
    TIME_LIMIT = 30 * 60  # 30 minutes
else:
    ENV = LocalEnvironment(processes=12)
    SUITE = [
        "gripper:prob01.pddl",
        "gripper:prob10.pddl",
    ]
    TIME_LIMIT = 3
ATTRIBUTES = [
    "run_dir",
    "coverage",
    "unsolvable",
    "out_of_memory",
    "out_of_time",
    "search_time",
    "total_time",
    "num_generated",
    "num_expanded",
    "num_expanded_until_last_f_layer",
    "num_generated_until_last_f_layer",
    "num_pruned_until_last_f_layer",

    "num_reachable_fluent_atoms",
    "num_reachable_derived_atoms",

    "memory_in_bytes_for_unextended_state_portions",
    "memory_in_bytes_per_unextended_state_portion",
    "memory_in_bytes_for_extended_state_portions",
    "memory_in_bytes_per_extended_state_portion",
    "memory_in_bytes_for_states",
    "memory_in_bytes_per_state",
    "memory_in_bytes_for_nodes",
    "memory_in_bytes_per_node",
    "memory_in_bytes_for_actions",
    "memory_in_bytes_per_action",
    "memory_in_bytes_for_axioms",
    "memory_in_bytes_per_axiom",
    "total_memory_in_bytes",

    "num_of_states",
    "num_of_nodes",
    "num_of_actions",
    "num_of_axioms",

    "cost",
    "length",
    "invalid_plan_reported",
]

MEMORY_LIMIT = 8000

# Create a new experiment.
exp = Experiment(environment=ENV)
exp.add_parser(AStarParser())

exp.add_resource("fast_downward_py", str(REPO / "fast-downward.py"))
exp.add_resource("driver", str(REPO / "driver"))
exp.add_resource("translator", str(REPO / "builds" / "release64" / "bin" / "translate"), str(Path("builds") / "release64" / "bin" / "translate"))
exp.add_resource("downward", str(REPO / "builds" / "release64" / "bin" / "downward"), str(Path("builds") / "release64" / "bin" / "downward"))
exp.add_resource("preprocess", str(REPO / "builds" / "release64" / "bin" / "preprocess"), str(Path("builds") / "release64" / "bin" / "preprocess"))
exp.add_resource("run_planner", DIR / "run_planner.sh")

for task in suites.build_suite(BENCHMARKS_DIR, SUITE):
    run = exp.add_run()
    run.add_resource("domain", task.domain_file, symlink=True)
    run.add_resource("problem", task.problem_file, symlink=True)
    # 'ff' binary has to be on the PATH.
    # We could also use exp.add_resource().
    run.add_command(
        "astar_planner",
        ["{run_planner}", "{fast_downward_py}", "{domain}", "{problem}", "sas_plan"],
        time_limit=TIME_LIMIT,
        memory_limit=MEMORY_LIMIT,
    )
    # AbsoluteReport needs the following properties:
    # 'domain', 'problem', 'algorithm', 'coverage'.
    run.set_property("domain", task.domain)
    run.set_property("problem", task.problem)
    run.set_property("algorithm", "numeric-downward-astar-blind")
    # BaseReport needs the following properties:
    # 'time_limit', 'memory_limit'.
    run.set_property("time_limit", TIME_LIMIT)
    run.set_property("memory_limit", MEMORY_LIMIT)
    # Every run has to have a unique id in the form of a list.
    # The algorithm name is only really needed when there are
    # multiple algorithms.
    run.set_property("id", ["numeric-downward-astar-blind", task.domain, task.problem])

# Add step that writes experiment files to disk.
exp.add_step("build", exp.build)

# Add step that executes all runs.
exp.add_step("start", exp.start_runs)

exp.add_step("parse", exp.parse)

# Add step that collects properties from run directories and
# writes them to *-eval/properties.
exp.add_fetcher(name="fetch")

# Make a report.
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="report.html")

# Parse the commandline and run the specified steps.
exp.run_steps()