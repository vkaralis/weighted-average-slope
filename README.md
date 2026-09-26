# Weighted Average Slope for Drug-Absorption Rate

A standalone, dependency-free Python implementation of **weighted average
slope (weighted AS or ASw)** from observed concentration-time data. It uses
all consecutive observations from `t = 0` through observed `Tmax`, inclusive,
and places progressively greater emphasis on the earlier intervals.

## Definition

For `n` observations up to and including `Tmax`:

```text
slope[i]  = (C[i+1] - C[i]) / (t[i+1] - t[i])
weight[i] = (Tmax - t[i]) / Tmax

                         1       n-1
weighted average slope = ----- ×  Σ  weight[i] × slope[i]
                        n - 1     i=1
```

The weight uses the **left-hand time** of each interval. The denominator is
`n - 1`, the number of intervals; the weights are **not normalized by their
sum**. This detail is important because normalizing by `sum(weight)` would
produce a different metric from the published ASw definition.

The units of weighted AS are concentration/time. Compared with the unweighted
AS, it emphasizes early observations, where the concentration-time profile is
more strongly associated with the absorption process.

The definition follows:

> Karalis VD. On the Interplay between Machine Learning, Population
> Pharmacokinetics, and Bioequivalence to Introduce Average Slope as a New
> Measure for Absorption Rate. *Applied Sciences*. 2023;13(4):2257.
> <https://doi.org/10.3390/app13042257>

## Install

Python 3.9 or newer is required.

```bash
python -m pip install .
```

Run the tests without third-party testing packages:

```bash
python -m unittest discover -s tests -v
```

## Python API

```python
from weighted_average_slope import weighted_average_slope

result = weighted_average_slope(
    times=[0, 0.5, 1.5, 3, 5],
    concentrations=[0, 2, 6, 9, 7],
)

print(result.weighted_average_slope)  # 2.7777777777777777
print(result.tmax)                    # 3.0
print(result.interval_slopes)         # (4.0, 4.0, 2.0)
print(result.interval_weights)        # (1.0, 0.833..., 0.5)
```

## CSV command line

The bundled example contains two subjects:

```bash
weighted-average-slope examples/concentration_time.csv --group subject
```

Write results to a CSV file:

```bash
weighted-average-slope input.csv --group subject --output weighted_as_results.csv
```

Use different column names:

```bash
weighted-average-slope input.csv --time TIME --concentration CONC --group ID
```

The output includes ASw, Cmax, Tmax, the number of points, and semicolon-
separated slopes, weights, and weighted slopes so that every calculation can
be audited. Input rows may be unordered; the CLI sorts each group by time.

## Data rules and explicit choices

- Time must start at exactly `0`, be finite, non-negative, and strictly
  increasing within a profile.
- Concentrations must be finite and non-negative.
- At least one post-dose point is required before or at the peak.
- The first occurrence of a tied observed Cmax defines Tmax by default. Use
  `--tmax-tie last` to select the last occurrence or `--tmax-tie error` to
  reject ties.
- Missing and BLQ values are rejected rather than silently imputed. Apply and
  document the preprocessing rule specified in the analysis plan first.
- ASw is calculated independently for each profile/subject. Concentrations
  should not be averaged across subjects before calculation.

This software implements a calculation and is not validated for clinical or
regulatory decision-making. Users are responsible for data review, validation,
pre-specified handling rules, and compliance with applicable guidance.

## Repository contents

```text
src/weighted_average_slope/  library and CLI
tests/                       unit and CLI tests
examples/                    example concentration-time CSV
CITATION.cff                 citation metadata
LICENSE                      MIT license
.github/workflows/           automated tests on GitHub
```

