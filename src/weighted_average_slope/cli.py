"""Command-line interface for weighted-average-slope-pk."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Sequence

from .core import weighted_average_slope


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate weighted average slope from t=0 through Tmax."
    )
    parser.add_argument("input", type=Path, help="Input CSV file")
    parser.add_argument("--time", default="time", help="Time column (default: time)")
    parser.add_argument(
        "--concentration",
        default="concentration",
        help="Concentration column (default: concentration)",
    )
    parser.add_argument(
        "--group",
        help="Optional grouping column, e.g. subject; one result per group",
    )
    parser.add_argument(
        "--tmax-tie",
        choices=("first", "last", "error"),
        default="first",
        help="Rule for repeated Cmax values (default: first)",
    )
    parser.add_argument("--output", type=Path, help="Write results to this CSV")
    parser.add_argument(
        "--json", action="store_true", help="Print results as JSON instead of CSV"
    )
    return parser


def _read_groups(path: Path, time_col: str, conc_col: str, group_col: str | None):
    groups: dict[str, list[tuple[float, float]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {time_col, conc_col} | ({group_col} if group_col else set())
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"missing CSV column(s): {', '.join(sorted(missing))}")
        for line_number, row in enumerate(reader, start=2):
            try:
                key = row[group_col] if group_col else "all"
                groups[key].append((float(row[time_col]), float(row[conc_col])))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid numeric value on CSV line {line_number}") from exc
    if not groups:
        raise ValueError("input CSV has no data rows")
    return groups


def _joined(values: tuple[float, ...]) -> str:
    return ";".join(str(value) for value in values)


def run(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    groups = _read_groups(args.input, args.time, args.concentration, args.group)
    rows = []
    for key, observations in groups.items():
        observations.sort(key=lambda pair: pair[0])
        result = weighted_average_slope(
            (pair[0] for pair in observations),
            (pair[1] for pair in observations),
            tmax_tie=args.tmax_tie,
        )
        rows.append(
            {
                "group": key,
                "weighted_average_slope": result.weighted_average_slope,
                "cmax": result.cmax,
                "tmax": result.tmax,
                "n_points": result.n_points,
                "interval_slopes": _joined(result.interval_slopes),
                "interval_weights": _joined(result.interval_weights),
                "weighted_interval_slopes": _joined(
                    result.weighted_interval_slopes
                ),
            }
        )

    fieldnames = list(rows[0])
    if args.output:
        with args.output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    elif args.json:
        print(json.dumps(rows, indent=2))
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return 0


def main() -> None:
    try:
        raise SystemExit(run())
    except (OSError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from exc


if __name__ == "__main__":
    main()

