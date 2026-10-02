import numpy as np  # type: ignore


def to_rotating_frame(t: np.ndarray, xy: np.ndarray, omega: float) -> np.ndarray:
    """
    xy has shape (N,2), inertial-frame positions at times t (shape (N,)).
    Rotate each point by angle -omega*t (i.e. undo the frame's rotation) to
    get the co-rotating-frame coordinates:
      x_rot = x*cos(omega*t) + y*sin(omega*t)
      y_rot = -x*sin(omega*t) + y*cos(omega*t)
    Return shape (N,2). Vectorize with numpy, no Python loop.
    """
    t = np.asarray(t, dtype=float)
    xy = np.asarray(xy, dtype=float)
    if t.ndim != 1 or xy.ndim != 2 or xy.shape != (len(t), 2):
        raise ValueError("t must have shape (N,) and xy must have shape (N, 2).")
    if (
        not np.isfinite(omega)
        or not np.all(np.isfinite(t))
        or not np.all(np.isfinite(xy))
    ):
        raise ValueError("Frame inputs must contain only finite values.")

    theta = omega * t
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    x = xy[:, 0]
    y = xy[:, 1]

    x_rot = x * cos_theta + y * sin_theta
    y_rot = -x * sin_theta + y * cos_theta

    return np.column_stack((x_rot, y_rot))
