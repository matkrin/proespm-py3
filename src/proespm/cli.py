import argparse
from dataclasses import dataclass
import logging
from pathlib import Path
import sys
import tomllib
from typing import cast

import matplotlib.pyplot as plt
from proespm.config import Config
from proespm.processing import (
    create_html,
    create_measurement_objs,
    process_loop,
)


@dataclass
class Args:
    data_dir: Path
    output: Path | None
    colormap: str
    colorrange_start: float
    colorrange_end: float
    verbose: int
    version: bool


def run_cli() -> None:
    args = parse_args()

    data_dir = args.data_dir.resolve()
    if not data_dir.exists():
        print(f"No such directory: {data_dir}", file=sys.stderr)
        sys.exit(1)

    if args.colormap not in plt.colormaps():
        print(f"No such colormap '{args.colormap}'", file=sys.stderr)
        sys.exit(1)

    if args.colorrange_start < 0 or args.colorrange_start > 100:
        print(
            "Start of color range must be between 0.0 and 100.0",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.colorrange_end < 0 or args.colorrange_end > 100:
        print(
            "End of color range must be between 0.0 and 100.0", file=sys.stderr
        )
        sys.exit(1)

    log_format = "[%(asctime)s %(levelname)s %(name)s]: %(message)s"
    log_level = determine_log_level(args.verbose)
    logging.basicConfig(format=log_format, level=log_level)

    colorrange = (args.colorrange_start, args.colorrange_end)

    output_path = args.output
    if output_path is None:
        output_path = data_dir.parent / f"{data_dir.name}_report.html"

    report_name = args.data_dir.name

    config = Config(colormap=args.colormap, colorrange=colorrange)
    print(f"Start processing of {data_dir}")
    process_objs = create_measurement_objs(str(data_dir), print)
    process_loop(process_objs, config, print)
    create_html(process_objs, str(output_path), report_name)
    print(f"HTML created at {output_path}")


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="proespm",
        description="Creation of HTML reports of scientifc data",
    )
    _ = parser.add_argument(
        "data_dir",
        type=Path,
        help="Directory containing data to process",
    )
    _ = parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path of the created HTML report (default: parent directory of data_dir)",
    )
    _ = parser.add_argument(
        "-c",
        "--colormap",
        type=str,
        default="inferno",
        help="Matplotlib colormap used for microsopy data (default: %(default)s)",
    )
    _ = parser.add_argument(
        "-s",
        "--colorrange-start",
        type=float,
        default=0.1,
        help="Percentile start of color range for microscopy data (default: %(default)s)",
    )
    _ = parser.add_argument(
        "-e",
        "--colorrange-end",
        type=float,
        default=99.9,
        help="Percentile end of color range for microscopy data (default: %(default)s)",
    )
    _ = parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (up to -vvv)",
    )
    _ = parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Print version",
    )

    return Args(**vars(parser.parse_args()))  # pyright: ignore[reportAny]


def get_version() -> str:
    """Get the version of this package as defined in pyproject.toml."""

    source_location = Path(__file__).parent.parent.parent
    pyproject = source_location / "pyproject.toml"
    if pyproject.exists():
        with open(pyproject, "rb") as f:
            return cast(str, tomllib.load(f)["project"]["version"])

    return ""


def determine_log_level(verbosity: int) -> int:
    if verbosity == 1:
        log_level = logging.WARN
    elif verbosity == 2:
        log_level = logging.INFO
    elif verbosity > 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR

    return log_level
