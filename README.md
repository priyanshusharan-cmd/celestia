<div align="center">
  <h1>✦ Celestia: Orbital Dynamics Laboratory</h1>
  <p><strong>Cosmic Code Hackathon 2026 Submission</strong></p>
</div>

---

## 🎥 Demo Video
> **[Watch the Demo Video Here](./Demo.mov)**

## 🌌 Overview
**Celestia** is an interactive, scientifically rigorous orbital dynamics laboratory. It allows users to simulate the Circular Restricted Three-Body Problem (CR3BP), seamlessly identifying and visualizing the five Lagrange points (L1–L5) for any two massive bodies in the Solar System or beyond.

With real-time numerical integration and a cinematic rendering engine, Celestia demonstrates exactly how a satellite behaves when placed near these points of gravitational equilibrium, all wrapped in a premium, immersive user interface.

## ✨ Features
- **Live Interactive Telemetry:** Adjust masses, separation, and satellite perturbations on the fly using a high-performance Streamlit interface.
- **Customizable Planetary Systems:** Choose from our Solar System catalog or create completely custom planetary bodies by clicking on the orbital map.
- **Real-time Orbital Integration:** Powered by the `REBOUND` N-body integrator using the high-accuracy IAS15 integrator.
- **Multi-Layer Field Maps:** Toggle between 2D Orbital Plane maps and 3D Potential Terrain layers to understand the gravitational landscape.
- **Cinematic Exports:** Render ultra-high-quality animations of your satellite's trajectory using `Manim`, triggered directly from the web interface.

## 🔭 Scientific Approach
- **Physics Model:** The simulation is built on the Circular Restricted Three-Body Problem (CR3BP).
- **Lagrange Points:** Calculated dynamically based on the mass ratio $\mu = \frac{m_2}{m_1 + m_2}$ of the primary and secondary bodies.
- **Stability Analysis:** Real-time classification of the equilibrium regions (Stable vs Unstable Saddle points).
- **Integration:** The `rebound_sim.py` module sets up the CR3BP in a normalized inertial frame and calculates the orbital period. The satellite's initial state is transformed from the rotating frame, integrated over multiple periods, and transformed back for visualization.

## 🛠️ Built With
* **[Python 3](https://www.python.org/)** - Core language
* **[Streamlit](https://streamlit.io/)** - For the interactive live workspace UI
* **[REBOUND](https://rebound.readthedocs.io/)** - For high-precision N-body physics integration
* **[Manim](https://www.manim.community/)** - For the main simulation animation and visual physics rendering
* **[Plotly](https://plotly.com/python/)** - For interactive orbital mapping
* **[NumPy](https://numpy.org/)** - For matrix transformations and mathematics

## 🚀 How to Run

### 1. Prerequisites
Ensure you have Python installed, along with `ffmpeg` (required for Manim's video rendering).

### 2. Install Dependencies
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 3. Launch Celestia
Run the Streamlit application from the root directory:
```bash
streamlit run app.py
```

### 4. Mission Control Guide
1. **Configure System Parameters:** Select your primary and secondary bodies from the sidebar, or use the custom option to define exact masses and distances.
2. **Place the Satellite:** Select a target Lagrange point (L1-L5) and apply perturbation trims (Move in/out, Move sideways) to offset the satellite.
3. **Observe the Map:** Watch the resulting trajectory play out in the rotating reference frame. Check the Telemetry readout for the Jacobi Constant and maximum deviation.
4. **Render Simulation:** Click **"Export Video"** to render a high-quality Manim animation of the simulation.

---
<div align="center">
  <i>Build Boldly. Think Beyond the Obvious.</i><br>
  Developed for Singularity – The Astronomical Society of BMSCE
</div>
