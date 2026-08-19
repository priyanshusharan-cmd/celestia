import numpy as np
from scipy.optimize import brentq, newton


def mass_ratio(m1: float, m2: float) -> float:
    """Returns mu = m2 / (m1 + m2). Raises ValueError if m1<=0 or m2<=0."""
    if m1 <= 0 or m2 <= 0:
        raise ValueError("Masses must be strictly positive.")
    return m2 / (m1 + m2)

def primary_positions(mu: float) -> tuple[float, float]:
    """Returns (x1, x2): positions of the two primaries on the x-axis in
    normalized CR3BP units, barycenter at origin. x1 = -mu, x2 = 1 - mu."""
    return -mu, 1.0 - mu

def effective_potential(x: float, y: float, mu: float) -> float:
    """Omega(x,y) = (1-mu)/r1 + mu/r2 + (x**2 + y**2)/2
    where r1 = distance to primary 1 at (-mu, 0), r2 = distance to primary 2
    at (1-mu, 0). Add a small epsilon (1e-9) to r1, r2 before dividing to
    avoid division by zero exactly at a primary."""
    x1, x2 = primary_positions(mu)
    r1 = np.sqrt((x - x1)**2 + y**2) + 1e-9
    r2 = np.sqrt((x - x2)**2 + y**2) + 1e-9
    return (1.0 - mu) / r1 + mu / r2 + (x**2 + y**2) / 2.0

def collinear_equation(x: float, mu: float) -> float:
    """The derivative dOmega/dx evaluated at y=0, as a function of x only.
    This is what we root-find for L1, L2, L3. Derive it analytically as:
    x - (1-mu)*(x+mu)/abs(x+mu)**3 - mu*(x-1+mu)/abs(x-1+mu)**3
    (this is the standard CR3BP collinear-point equation; do not simplify
    it further, use it exactly as given)."""
    return x - (1.0 - mu)*(x + mu)/abs(x + mu)**3 - mu*(x - 1.0 + mu)/abs(x - 1.0 + mu)**3

def find_L1(mu: float) -> float:
    """Root of collinear_equation between the two primaries. Use
    scipy.optimize.brentq with bracket (-mu + 1e-6, 1 - mu - 1e-6).
    If that bracket fails, search more narrowly around x = 1 - mu - (mu/3)**(1/3)
    as a starting guess with scipy.optimize.newton instead."""
    try:
        try:
            return brentq(collinear_equation, -mu + 1e-6, 1.0 - mu - 1e-6, args=(mu,))
        except ValueError:
            guess = 1.0 - mu - (mu/3.0)**(1/3.0)
            return newton(collinear_equation, guess, args=(mu,))
    except ValueError as e:
        raise ValueError("Mass ratio out of supported range for stable L-point finding") from e

def find_L2(mu: float) -> float:
    """Root of collinear_equation beyond the smaller body (x > 1 - mu).
    Use scipy.optimize.brentq with bracket (1 - mu + 1e-6, 2.0)."""
    try:
        return brentq(collinear_equation, 1.0 - mu + 1e-6, 2.0, args=(mu,))
    except ValueError as e:
        raise ValueError("Mass ratio out of supported range for stable L-point finding") from e

def find_L3(mu: float) -> float:
    """Root of collinear_equation beyond the larger body (x < -mu).
    Use scipy.optimize.brentq with bracket (-2.0, -mu - 1e-6)."""
    try:
        return brentq(collinear_equation, -2.0, -mu - 1e-6, args=(mu,))
    except ValueError as e:
        raise ValueError("Mass ratio out of supported range for stable L-point finding") from e

def L4_L5(mu: float) -> tuple[tuple[float,float], tuple[float,float]]:
    """Returns (L4, L5) as ((x,y), (x,y)) using the closed form:
    x = 0.5 - mu, y = sqrt(3)/2 for L4, y = -sqrt(3)/2 for L5."""
    x = 0.5 - mu
    y = np.sqrt(3.0)/2.0
    return ((x, y), (x, -y))

def all_lagrange_points(mu: float) -> dict:
    """Returns {'L1': (x,0.0), 'L2': (x,0.0), 'L3': (x,0.0), 'L4': (x,y),
    'L5': (x,y)} using the functions above."""
    l1_x = find_L1(mu)
    l2_x = find_L2(mu)
    l3_x = find_L3(mu)
    l4, l5 = L4_L5(mu)
    return {
        'L1': (l1_x, 0.0),
        'L2': (l2_x, 0.0),
        'L3': (l3_x, 0.0),
        'L4': l4,
        'L5': l5
    }

def stability(mu: float, point_xy: tuple[float, float]) -> dict:
    """Classify stability of a Lagrange point via linearization.
    Compute the second partial derivatives of effective_potential at
    point_xy numerically using central finite differences (step=1e-6):
    Oxx, Oyy, Oxy.
    Build the 4x4 system matrix A for the linearized rotating-frame
    equations of motion:
      state = [dx, dy, dvx, dvy]
      d/dt [dx,dy,dvx,dvy] = A @ [dx,dy,dvx,dvy]
      A = [[0,0,1,0],
           [0,0,0,1],
           [Oxx, Oxy, 0, 2],
           [Oxy, Oyy, -2, 0]]
    Compute eigenvalues of A with numpy.linalg.eigvals.
    Classify: if max(real part of eigenvalues) > 1e-6 -> 'unstable',
    else -> 'stable'.
    Return {'eigenvalues': eigenvalues (as list of complex),
            'classification': 'stable' or 'unstable'}."""
    x, y = point_xy
    h = 1e-6
    
    O_xy_base = effective_potential(x, y, mu)
    Oxx = (effective_potential(x+h, y, mu) - 2*O_xy_base + effective_potential(x-h, y, mu)) / (h**2)
    Oyy = (effective_potential(x, y+h, mu) - 2*O_xy_base + effective_potential(x, y-h, mu)) / (h**2)
    
    Oxy = (effective_potential(x+h, y+h, mu) - effective_potential(x+h, y-h, mu) 
           - effective_potential(x-h, y+h, mu) + effective_potential(x-h, y-h, mu)) / (4 * h**2)
           
    A = np.array([
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [Oxx, Oxy, 0, 2],
        [Oxy, Oyy, -2, 0]
    ])
    
    eigenvalues = np.linalg.eigvals(A)
    max_real = np.max(np.real(eigenvalues))
    
    classification = 'unstable' if max_real > 1e-6 else 'stable'
    
    return {
        'eigenvalues': eigenvalues.tolist(),
        'classification': classification
    }

def jacobi_constant(mu: float, x: float, y: float, vx: float, vy: float) -> float:
    """C = 2*effective_potential(x,y,mu) - (vx**2 + vy**2)"""
    return 2.0 * effective_potential(x, y, mu) - (vx**2 + vy**2)


if __name__ == "__main__":
    test_mu = 0.0121
    points = all_lagrange_points(test_mu)
    print(f"Testing for mu={test_mu}")
    for name, pt in points.items():
        stab = stability(test_mu, pt)
        print(f"{name}: classification={stab['classification']}, pt={pt}")
        print(f"  eigenvalues={stab['eigenvalues']}")
