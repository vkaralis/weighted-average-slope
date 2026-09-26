import math
import unittest

from weighted_average_slope import weighted_average_slope


class WeightedAverageSlopeTests(unittest.TestCase):
    def test_formula_with_irregular_sampling(self):
        result = weighted_average_slope(
            [0, 0.5, 1.5, 3, 5], [0, 2, 6, 9, 7]
        )
        self.assertEqual(result.tmax, 3)
        self.assertEqual(result.cmax, 9)
        self.assertEqual(result.n_points, 4)
        self.assertEqual(result.interval_slopes, (4.0, 4.0, 2.0))
        expected_weights = (1.0, 2.5 / 3.0, 0.5)
        for actual, expected in zip(result.interval_weights, expected_weights):
            self.assertTrue(math.isclose(actual, expected))
        self.assertTrue(math.isclose(result.weighted_average_slope, 25 / 9))

    def test_divides_by_interval_count_not_sum_of_weights(self):
        result = weighted_average_slope([0, 1, 2, 3, 4], [0, 3, 5, 6, 4])
        self.assertTrue(math.isclose(result.weighted_average_slope, 14 / 9))
        self.assertFalse(
            math.isclose(
                result.weighted_average_slope,
                sum(result.weighted_interval_slopes) / sum(result.interval_weights),
            )
        )

    def test_only_observations_through_tmax_are_used(self):
        result = weighted_average_slope([0, 1, 2, 3], [0, 4, 3, 1])
        self.assertEqual(result.interval_slopes, (4.0,))
        self.assertEqual(result.interval_weights, (1.0,))
        self.assertEqual(result.weighted_average_slope, 4.0)

    def test_tied_cmax_rules(self):
        first = weighted_average_slope([0, 1, 2, 3], [0, 5, 5, 2])
        last = weighted_average_slope(
            [0, 1, 2, 3], [0, 5, 5, 2], tmax_tie="last"
        )
        self.assertEqual(first.tmax, 1)
        self.assertEqual(first.weighted_average_slope, 5)
        self.assertEqual(last.tmax, 2)
        self.assertEqual(last.weighted_average_slope, 2.5)
        with self.assertRaisesRegex(ValueError, "more than one time"):
            weighted_average_slope(
                [0, 1, 2, 3], [0, 5, 5, 2], tmax_tie="error"
            )

    def test_invalid_inputs(self):
        cases = [
            ([1, 2], [0, 1], "t=0"),
            ([0, 1, 1], [0, 1, 2], "strictly increasing"),
            ([0, 1], [0, -1], "non-negative"),
            ([0], [0], "at least two"),
            ([0, 1], [0], "same length"),
        ]
        for times, concentrations, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    weighted_average_slope(times, concentrations)

    def test_tmax_at_zero_is_not_computable(self):
        with self.assertRaisesRegex(ValueError, "Tmax is t=0"):
            weighted_average_slope([0, 1, 2], [4, 3, 2])


if __name__ == "__main__":
    unittest.main()

