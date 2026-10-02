import re
import shutil
import tempfile
import threading
import uuid
from pathlib import Path

import numpy as np  # type: ignore
from manim import (  # type: ignore
    BOLD,
    DOWN,
    PI,
    WHITE,
    Circle,
    Dot,
    Scene,
    Text,
    TracedPath,
    ValueTracker,
    VGroup,
    VMobject,
    linear,
    tempconfig,
)

_RENDER_LOCK = threading.Lock()
_RENDER_PREFIX = "celestia-render-"


class OrbitalScene(Scene):
    def __init__(
        self, mu, trajectory, body1_name, body2_name, m1_mass, m2_mass, **kwargs
    ):
        super().__init__(**kwargs)
        self.mu = mu
        self.trajectory = trajectory
        self.body1_name = body1_name
        self.body2_name = body2_name
        self.m1_mass = m1_mass
        self.m2_mass = m2_mass

    def construct(self):
        # Deep space background
        self.camera.background_color = "#040812"

        # Keep the background lightweight enough for small hosted instances.
        np.random.seed(42)
        star_colors = ["#ffffff", "#eaf0ff", "#9e8cff", "#72e6de"]
        stars = VGroup(
            *[
                Dot(
                    np.array([np.random.uniform(-10, 10), np.random.uniform(-6, 6), 0]),
                    radius=np.random.uniform(0.01, 0.04),
                    color=np.random.choice(star_colors),
                    fill_opacity=np.random.uniform(0.1, 0.9),
                )
                for _ in range(140)
            ]
        )
        self.add(stars)

        if self.trajectory is None or len(self.trajectory) == 0:
            return

        points = self.trajectory * 3.0
        points_3d = np.column_stack((points, np.zeros(len(points))))

        # Compute radius based on mass
        def get_radius(m):
            log_m = np.log10(max(float(m), 1e-5))
            frac = np.clip((log_m + 2.0) / 7.7, 0.0, 1.0)
            return 0.15 + frac * 0.45

        r1 = get_radius(self.m1_mass)
        r2 = get_radius(self.m2_mass)

        def create_glowing_body(radius, color, glow_color):
            body = VGroup()
            # Glow layers
            for i in range(4, 0, -1):
                glow = Circle(
                    radius=radius + i * 0.12,
                    color=glow_color,
                    stroke_width=0,
                    fill_opacity=0.06,
                )
                body.add(glow)
            # Core
            core = Circle(radius=radius, color=color, stroke_width=0, fill_opacity=1.0)
            body.add(core)
            return body

        # Create bodies and labels
        p1 = create_glowing_body(r1, "#ffd166", "#ffa700")
        p1_label = Text(
            self.body1_name, font_size=22, weight=BOLD, color=WHITE
        ).set_opacity(0.8)

        p2 = create_glowing_body(r2, "#5eead4", "#00b4d8")
        p2_label = Text(
            self.body2_name, font_size=18, weight=BOLD, color=WHITE
        ).set_opacity(0.8)

        probe = Dot(color="#ffffff", radius=0.07)
        probe_glow = Circle(
            radius=0.18, color="#72e6de", stroke_width=0, fill_opacity=0.3
        )
        probe_group = VGroup(probe_glow, probe)

        # Trace path inside the rotating frame (subtle)
        rotating_path = VMobject()
        rotating_path.set_stroke(color="#8291b0", width=1.2, opacity=0.35)

        self.add(rotating_path, p1, p2, probe_group, p1_label, p2_label)

        tracker = ValueTracker(0)
        total_angle = 6 * PI

        def update_objects(m):
            val = tracker.get_value()
            angle = val * total_angle
            idx = int(val * (len(points) - 1))

            # Rotate bodies
            p1_pos = (
                np.array([-self.mu * np.cos(angle), -self.mu * np.sin(angle), 0]) * 3
            )
            p1.move_to(p1_pos)
            p1_label.move_to(p1_pos + DOWN * (r1 + 0.6))

            p2_pos = (
                np.array(
                    [(1 - self.mu) * np.cos(angle), (1 - self.mu) * np.sin(angle), 0]
                )
                * 3
            )
            p2.move_to(p2_pos)
            p2_label.move_to(p2_pos + DOWN * (r2 + 0.5))

            # Rotate the path using vectorized numpy operations
            c, s = np.cos(angle), np.sin(angle)
            rot_mat = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
            rotated_points = np.dot(points_3d, rot_mat.T)

            rotating_path.set_points_as_corners(rotated_points)

            # Update probe position
            probe_group.move_to(rotated_points[idx])

        p1.add_updater(update_objects)

        # Add inertial trace behind the probe
        try:
            inertial_trace = TracedPath(
                probe.get_center,
                dissipating_time=1.2,
                stroke_width=3.5,
                stroke_color="#72e6de",
                stroke_opacity=0.9,
            )
        except TypeError:
            # Fallback if dissipating_time is not supported in this version
            inertial_trace = TracedPath(
                probe.get_center,
                stroke_width=3.5,
                stroke_color="#72e6de",
                stroke_opacity=0.9,
            )

        self.add(inertial_trace)

        self.play(tracker.animate.set_value(1), run_time=4.0, rate_func=linear)
        self.wait(0.4)


def render_trajectory(
    mu, trajectory, output_file, body1_name, body2_name, m1_mass, m2_mass
):
    trajectory = np.asarray(trajectory, dtype=float)
    if trajectory.ndim != 2 or trajectory.shape[1] != 2 or len(trajectory) < 2:
        raise ValueError("Trajectory must contain at least two x/y positions.")
    if len(trajectory) > 10_000 or not np.all(np.isfinite(trajectory)):
        raise ValueError("Trajectory is too large or contains invalid values.")
    if len(trajectory) > 320:
        sample_indices = np.linspace(0, len(trajectory) - 1, 320, dtype=int)
        trajectory = trajectory[sample_indices]

    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "-", Path(output_file).stem).strip("-")
    safe_stem = (safe_stem or "orbital-simulation")[:48]
    unique_output = f"{safe_stem}-{uuid.uuid4().hex[:10]}"
    media_dir = Path(tempfile.mkdtemp(prefix=_RENDER_PREFIX))

    try:
        # Manim configuration is process-global, so serialize renders while still
        # giving every session a private output directory and filename.
        with (
            _RENDER_LOCK,
            tempconfig(
                {
                    "media_dir": str(media_dir),
                    "output_file": unique_output,
                    "format": "mp4",
                    "pixel_width": 854,
                    "pixel_height": 480,
                    "frame_rate": 24,
                    "verbosity": "ERROR",
                    "disable_caching": True,
                }
            ),
        ):
            scene = OrbitalScene(
                mu,
                trajectory,
                str(body1_name)[:80],
                str(body2_name)[:80],
                m1_mass,
                m2_mass,
            )
            scene.render()
            movie_path = Path(scene.renderer.file_writer.movie_file_path).resolve()
        if not movie_path.is_file() or media_dir.resolve() not in movie_path.parents:
            raise RuntimeError("Manim did not create the expected video output.")
        return str(movie_path)
    except Exception:
        shutil.rmtree(media_dir, ignore_errors=True)
        raise


def cleanup_render(video_path: str | None) -> None:
    """Remove only a render directory created by this module."""
    if not video_path:
        return
    candidate = Path(video_path).resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    for parent in (candidate.parent, *candidate.parents):
        if parent.parent == temp_root and parent.name.startswith(_RENDER_PREFIX):
            shutil.rmtree(parent, ignore_errors=True)
            return
