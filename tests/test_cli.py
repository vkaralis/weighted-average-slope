import csv
import tempfile
import unittest
from pathlib import Path

from weighted_average_slope.cli import run


class CliTests(unittest.TestCase):
    def test_cli_calculates_each_subject(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            source.write_text(
                "subject,time,concentration\nA,0,0\nA,1,2\nA,2,1\n"
                "B,0,0\nB,1,3\nB,2,6\nB,3,4\n",
                encoding="utf-8",
            )
            output = Path(directory) / "result.csv"
            self.assertEqual(
                run([str(source), "--group", "subject", "--output", str(output)]), 0
            )
            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual([row["group"] for row in rows], ["A", "B"])
            self.assertEqual(
                [float(row["weighted_average_slope"]) for row in rows],
                [2.0, 2.25],
            )
            self.assertIn("interval_weights", rows[0])
            self.assertIn("weighted_interval_slopes", rows[0])


if __name__ == "__main__":
    unittest.main()

