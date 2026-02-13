import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

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


def run_cli() -> None:
    args = parse_args()

    data_dir = args.data_dir.resolve()
    if not data_dir.exists():
        print(f"No such directory: {data_dir}", file=sys.stderr)
        sys.exit(1)

    if args.colormap not in plt.colormaps():
        print(f"No such colormap '{args.colormap}'")
        sys.exit(1)

    if args.colorrange_start < 0 or args.colorrange_start > 100:
        print("Start of color range must be between 0.0 and 100.0")
        sys.exit(1)

    if args.colorrange_end < 0 or args.colorrange_end > 100:
        print("End of color range must be between 0.0 and 100.0")
        sys.exit(1)

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


def parse_args() -> type[Args]:
    parser = argparse.ArgumentParser(
        prog="proespm",
        description="Creation of HTML reports of scientifc data",
    )
    _ = parser.add_argument(
        "data_dir", type=Path, help="Directory containing data to process"
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

    return parser.parse_args(namespace=Args)
