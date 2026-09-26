"""Compatibility installer for Python environments with older build tooling."""

from setuptools import find_packages, setup


setup(
    name="weighted-average-slope-pk",
    version="0.1.0",
    description="Weighted average slope through observed Tmax",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "weighted-average-slope=weighted_average_slope.cli:main"
        ]
    },
)

