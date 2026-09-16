"""CLI argument parsing and command routing."""

import argparse
import sys
from . import suite


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="promptlab",
        description="Command-line test runner for prompts"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a test suite")
    run_parser.add_argument("--suite", required=True, help="Path to suite JSON file")
    run_parser.add_argument("--runs", type=int, default=None, help="Number of runs per case")
    run_parser.add_argument("--out", default=None, help="Path to output report JSON")
    run_parser.add_argument("--report", action="store_true", help="Print human-readable summary")
    run_parser.set_defaults(func=run_command)

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two reports")
    compare_parser.add_argument("--baseline", required=True, help="Path to baseline report JSON")
    compare_parser.add_argument("--candidate", required=True, help="Path to candidate report JSON")
    compare_parser.add_argument("--out", default=None, help="Path to output diff JSON")
    compare_parser.set_defaults(func=compare_command)

    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Diagnostic utility")
    doctor_parser.set_defaults(func=doctor_command)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def run_command(args):
    """Handler for 'run' command."""
    try:
        from . import runner, report
        import json

        # Load and validate suite
        suite_data = suite.load_suite(args.suite)

        # Determine number of runs
        runs = args.runs if args.runs is not None else suite_data.get("runs", 1)

        # Execute suite
        cases_results, start_time, end_time = runner.run_suite(suite_data, runs)

        # Generate report
        report_data = report.generate_report(suite_data, cases_results, runs, start_time, end_time)

        # Output report
        if args.out:
            with open(args.out, 'w') as f:
                json.dump(report_data, f, indent=2, sort_keys=True)
        else:
            print(json.dumps(report_data, indent=2, sort_keys=True))

        # Print human summary if requested
        if args.report:
            report.print_human_summary(report_data, file=sys.stderr)

        # Exit code: 0 = all pass, 2 = any failure
        totals = report_data["totals"]
        if totals["failed"] > 0 or totals["flaky"] > 0:
            return 2
        return 0

    except FileNotFoundError as e:
        print(f"suite: cannot read file", file=sys.stderr)
        return 4
    except ValueError as e:
        print(f"suite: {str(e)}", file=sys.stderr)
        return 1


def compare_command(args):
    """Handler for 'compare' command."""
    try:
        # TODO: Implement comparison (Phase 3)
        print("Compare command not yet implemented", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def doctor_command(args):
    """Handler for 'doctor' command."""
    try:
        # TODO: Implement diagnostics (Phase 3)
        print("Doctor command not yet implemented", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
