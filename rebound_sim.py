# pylint: disable=missing-docstring, too-many-locals
import numpy as np  # type: ignore
import rebound  # type: ignore

import physics


def build_simulation(mu: float, m_total: float = 1.0, separation: float = 1.0):
    """
    Creates and returns a rebound.Simulation with G=1, in normalized CR3BP
    units.
    """
    sim = rebound.Simulation()
    sim.G = 1.0
    sim.integrator = "ias15"

    omega = np.sqrt(sim.G * m_total / (separation**3))

    m1 = (1.0 - mu) * m_total
    x1 = -mu * separation
    vy1 = omega * x1

    m2 = mu * m_total
    x2 = (1.0 - mu) * separation
    vy2 = omega * x2

    sim.add(m=m1, x=x1, y=0.0, vx=0.0, vy=vy1)
    sim.add(m=m2, x=x2, y=0.0, vx=0.0, vy=vy2)

    return sim


def add_satellite(sim, x: float, y: float, vx: float = 0.0, vy: float = 0.0):
    """Adds a massless test particle (m=0) to sim at the given position and
    velocity (in the same inertial frame/units as the primaries)."""
    sim.add(m=0.0, x=x, y=y, vx=vx, vy=vy)


def run_and_record(sim, t_end: float, n_samples: int = 500) -> dict:
    """
    Integrates sim from its current time to t_end, sampling n_samples
    evenly-spaced times.
    """
    times = np.linspace(sim.t, t_end, n_samples)

    p1_pos = np.zeros((n_samples, 2))
    p2_pos = np.zeros((n_samples, 2))
    sat_pos = np.zeros((n_samples, 2))

    for i, t in enumerate(times):
        sim.integrate(t)
        p1 = sim.particles[0]
        p2 = sim.particles[1]
        sat = sim.particles[-1]

        p1_pos[i] = [p1.x, p1.y]
        p2_pos[i] = [p2.x, p2.y]
        sat_pos[i] = [sat.x, sat.y]

        # Stop simulation if satellite is ejected far outside the map
        if np.sqrt(sat.x**2 + sat.y**2) > 3.5:
            times = times[: i + 1]
            p1_pos = p1_pos[: i + 1]
            p2_pos = p2_pos[: i + 1]
            sat_pos = sat_pos[: i + 1]
            break

    return {"t": times, "p1": p1_pos, "p2": p2_pos, "sat": sat_pos}


def main():
    test_mu = 0.0121
    sim = build_simulation(test_mu)

    # Get L4 coordinates from physics.py
    l_points = physics.all_lagrange_points(test_mu)
    l4_x, l4_y = l_points["L4"]

    # Calculate initial velocity for L4 in inertial frame (at rest in rotating frame)
    # G=1, m_total=1, separation=1 => omega = 1
    omega = 1.0
    vx = -omega * l4_y
    vy = omega * l4_x

    add_satellite(sim, x=l4_x, y=l4_y, vx=vx, vy=vy)

    # Run for two orbital periods
    period = 2.0 * np.pi / omega
    t_end = 2.0 * period

    data = run_and_record(sim, t_end=t_end, n_samples=500)

    # To check the distance from the starting point in the rotating frame,
    # we must rotate the inertial coordinates back to the rotating frame.
    theta = omega * data["t"]
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    sat_x_rot = data["sat"][:, 0] * cos_theta + data["sat"][:, 1] * sin_theta
    sat_y_rot = -data["sat"][:, 0] * sin_theta + data["sat"][:, 1] * cos_theta

    dist = np.sqrt((sat_x_rot - l4_x) ** 2 + (sat_y_rot - l4_y) ** 2)
    max_dist = np.max(dist)

    print(f"Max distance from L4 (in rotating frame) over 2 periods: {max_dist}")

if __name__ == "__main__":
    main()
