import numpy as np
from manim import *


class OrbitalScene(Scene):
    def __init__(self, mu, trajectory, body1_name, body2_name, m1_mass, m2_mass, **kwargs):
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

        # Create beautiful background stars
        np.random.seed(42)
        star_colors = ["#ffffff", "#eaf0ff", "#9e8cff", "#72e6de"]
        stars = VGroup(*[
            Dot(np.array([np.random.uniform(-10, 10), np.random.uniform(-6, 6), 0]), 
                radius=np.random.uniform(0.01, 0.04), 
                color=np.random.choice(star_colors), 
                fill_opacity=np.random.uniform(0.1, 0.9))
            for _ in range(400)
        ])
        self.add(stars)

        if self.trajectory is None or len(self.trajectory) == 0:
            return
            
        points = self.trajectory * 3.0
        
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
                glow = Circle(radius=radius + i * 0.12, color=glow_color, stroke_width=0, fill_opacity=0.06)
                body.add(glow)
            # Core
            core = Circle(radius=radius, color=color, stroke_width=0, fill_opacity=1.0)
            body.add(core)
            return body

        # Create bodies and labels
        p1 = create_glowing_body(r1, "#ffd166", "#ffa700")
        p1_label = Text(self.body1_name, font_size=22, weight=BOLD, color=WHITE).set_opacity(0.8)
        
        p2 = create_glowing_body(r2, "#5eead4", "#00b4d8")
        p2_label = Text(self.body2_name, font_size=18, weight=BOLD, color=WHITE).set_opacity(0.8)
        
        probe = Dot(color="#ffffff", radius=0.07)
        probe_glow = Circle(radius=0.18, color="#72e6de", stroke_width=0, fill_opacity=0.3)
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
            p1_pos = np.array([-self.mu * np.cos(angle), -self.mu * np.sin(angle), 0]) * 3
            p1.move_to(p1_pos)
            p1_label.move_to(p1_pos + DOWN * (r1 + 0.6))
            
            p2_pos = np.array([(1 - self.mu) * np.cos(angle), (1 - self.mu) * np.sin(angle), 0]) * 3
            p2.move_to(p2_pos)
            p2_label.move_to(p2_pos + DOWN * (r2 + 0.5))
            
            # Rotate the path using vectorized numpy operations
            c, s = np.cos(angle), np.sin(angle)
            rot_mat = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
            pts_3d = np.column_stack((points, np.zeros(len(points))))
            rotated_points = np.dot(pts_3d, rot_mat.T)
            
            rotating_path.set_points_as_corners(rotated_points)
            
            # Update probe position
            probe_group.move_to(rotated_points[idx])
            
        p1.add_updater(update_objects)
        
        # Add inertial trace behind the probe
        try:
            inertial_trace = TracedPath(probe.get_center, dissipating_time=1.2, stroke_width=3.5, stroke_color="#72e6de", stroke_opacity=0.9)
        except TypeError:
            # Fallback if dissipating_time is not supported in this version
            inertial_trace = TracedPath(probe.get_center, stroke_width=3.5, stroke_color="#72e6de", stroke_opacity=0.9)
            
        self.add(inertial_trace)
        
        self.play(tracker.animate.set_value(1), run_time=8.0, rate_func=linear)
        self.wait(1.5)

def render_trajectory(mu, trajectory, output_file, body1_name, body2_name, m1_mass, m2_mass):
    config.media_dir = "./manim_media"
    config.output_file = output_file
    config.format = "mp4"
    config.pixel_width = 1280
    config.pixel_height = 720
    config.frame_rate = 60
    
    scene = OrbitalScene(mu, trajectory, body1_name, body2_name, m1_mass, m2_mass)
    scene.render()
    return f"{config.media_dir}/videos/720p60/{output_file}.mp4"
