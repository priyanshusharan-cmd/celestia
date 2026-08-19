import numpy as np


def to_rotating_frame(t: np.ndarray, xy: np.ndarray, omega: float) -> np.ndarray:
    """
    xy has shape (N,2), inertial-frame positions at times t (shape (N,)).
    Rotate each point by angle -omega*t (i.e. undo the frame's rotation) to
    get the co-rotating-frame coordinates:
      x_rot = x*cos(omega*t) + y*sin(omega*t)
      y_rot = -x*sin(omega*t) + y*cos(omega*t)
    Return shape (N,2). Vectorize with numpy, no Python loop.
    """
    theta = omega * t
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    x = xy[:, 0]
    y = xy[:, 1]

    x_rot = x * cos_theta + y * sin_theta
    y_rot = -x * sin_theta + y * cos_theta

    return np.column_stack((x_rot, y_rot))
