import unittest

import numpy as np

import frames
import physics
import rebound_sim


class PhysicsTests(unittest.TestCase):
    def test_earth_sun_period_is_one_year(self):
        omega = physics.orbital_angular_velocity(
            physics.SOLAR_MASS_IN_EARTH_MASSES + 1.0, 1.0
        )
        period = 2.0 * np.pi / omega
        self.assertAlmostEqual(period, 1.0, places=5)

    def test_mass_ratio_rejects_non_finite_values(self):
        for invalid in (np.nan, np.inf, -np.inf):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                physics.mass_ratio(invalid, 1.0)

    def test_lagrange_solver_rejects_invalid_ratio(self):
        for invalid in (0.0, -0.1, 0.6, np.nan):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                physics.all_lagrange_points(invalid)


class FrameTests(unittest.TestCase):
    def test_rotating_frame_round_trip_for_quarter_orbit(self):
        t = np.array([0.0, np.pi / 2.0])
        inertial = np.array([[1.0, 0.0], [0.0, 1.0]])
        rotating = frames.to_rotating_frame(t, inertial, omega=1.0)
        np.testing.assert_allclose(rotating, [[1.0, 0.0], [1.0, 0.0]], atol=1e-12)

    def test_rotating_frame_rejects_mismatched_shapes(self):
        with self.assertRaises(ValueError):
            frames.to_rotating_frame(np.array([0.0]), np.zeros((2, 2)), omega=1.0)


class SimulationTests(unittest.TestCase):
    def test_scaled_l4_orbit_returns_to_same_normalized_position(self):
        mu = 0.0121
        separation = 2.0
        total_mass = 1.0123
        omega = physics.orbital_angular_velocity(total_mass, separation)
        l4 = np.array(physics.all_lagrange_points(mu)["L4"])
        dimensional_start = l4 * separation

        sim = rebound_sim.build_simulation(mu, total_mass, separation)
        rebound_sim.add_satellite(
            sim,
            dimensional_start[0],
            dimensional_start[1],
            -omega * dimensional_start[1],
            omega * dimensional_start[0],
        )
        period = 2.0 * np.pi / omega
        data = rebound_sim.run_and_record(
            sim, period, n_samples=80, escape_radius=3.5 * separation
        )
        rotating = frames.to_rotating_frame(data["t"], data["sat"], omega) / separation

        self.assertEqual(len(rotating), 80)
        self.assertLess(float(np.max(np.linalg.norm(rotating - l4, axis=1))), 1e-6)

    def test_recording_requires_a_satellite(self):
        sim = rebound_sim.build_simulation(0.0121)
        with self.assertRaises(ValueError):
            rebound_sim.run_and_record(sim, 1.0)


if __name__ == "__main__":
    unittest.main()
