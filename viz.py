import numpy as np
import plotly.graph_objects as go

import physics


def mass_to_size(m_earth: float, min_size: float = 6.0, max_size: float = 24.0) -> float:
    """Map a mass in Earth masses to a marker pixel size using log10 scale.
    Moon (0.0123) → ~8px   Earth (1) → ~16px   Sun (332946) → ~38px.
    Two equal masses always give the same size.
    """
    log_m = np.log10(max(float(m_earth), 1e-5))
    # log10 range anchors: -2 (sub-lunar) to 5.7 (Sun)
    frac = np.clip((log_m + 2.0) / 7.7, 0.0, 1.0)
    return min_size + frac * (max_size - min_size)


def add_map_click_grid(fig):
    """Invisible, selectable grid lets Streamlit return coordinates for map clicks."""
    ticks = np.linspace(-1.45, 1.45, 59)
    grid_x, grid_y = np.meshgrid(ticks, ticks)
    coords_x, coords_y = grid_x.ravel(), grid_y.ravel()
    fig.add_trace(go.Scatter(
        x=coords_x, y=coords_y, mode='markers',
        marker={'size': 12, 'color': 'rgba(0,0,0,0.003)'},
        customdata=[["map", round(float(x), 3), round(float(y), 3)] for x, y in zip(coords_x, coords_y)],
        hoverinfo='skip', showlegend=False, name='Map placement grid'
    ))


def add_playback_controls(fig):
    """Add unified playback controls: Play/Pause toggle, Timeline toggle, and Speed dropdown."""
    if len(fig.frames) < 2:
        return
        
    base_dur = 55
    speed_buttons = []
    for speed_label, mult in [("0.25X", 4), ("0.5X", 2), ("1X", 1), ("1.5X", 1/1.5), ("2X", 0.5), ("4X", 0.25), ("10X", 0.1)]:
        dur = int(base_dur * mult)
        speed_buttons.append({
            'label': speed_label,
            'method': 'animate',
            'args': [None, {"frame": {"duration": dur, "redraw": False}, "transition": {"duration": 0}, "mode": "immediate"}]
        })

    fig.update_layout(
        updatemenus=[
            {
                'type': 'buttons', 'direction': 'right', 'x': 0.015, 'y': 0.02, 'xanchor': 'left', 'yanchor': 'bottom',
                'bgcolor': 'rgba(13, 24, 52, .82)', 'bordercolor': 'rgba(114,230,222,.3)', 'borderwidth': 1,
                'showactive': False, 'font': {'color': '#72e6de', 'family': 'DM Mono', 'size': 11},
                'pad': {'r': 7, 't': 5, 'b': 5, 'l': 7},
                'buttons': [
                    {'label': '▶/Ⅱ', 'method': 'animate',
                     'args': [None, {"frame": {"duration": 55, "redraw": False}, "transition": {"duration": 0}, "fromcurrent": True, "mode": "immediate"}],
                     'args2': [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]},
                    {'label': '⚙ Timeline', 'method': 'relayout',
                     'args': [{'sliders[0].visible': True}],
                     'args2': [{'sliders[0].visible': False}]}
                ]
            },
            {
                'type': 'dropdown', 'direction': 'up', 'x': 0.26, 'y': 0.02, 'xanchor': 'left', 'yanchor': 'bottom',
                'bgcolor': 'rgba(13, 24, 52, .82)', 'bordercolor': 'rgba(114,230,222,.3)', 'borderwidth': 1,
                'active': 2, 'font': {'color': '#72e6de', 'family': 'DM Mono', 'size': 11},
                'pad': {'r': 7, 't': 5, 'b': 5, 'l': 7},
                'buttons': speed_buttons
            }
        ],
        sliders=[{
            'active': 0, 
            'steps': [{'method': 'animate', 'args': [[f.name], {'mode': 'immediate', 'frame': {'duration': 0, 'redraw': False}}]} for f in fig.frames],
            'visible': False, 
            'x': 0.015, 'y': -0.05, 'len': 0.97,
            'currentvalue': {'visible': False},
            'font': {'color': '#72e6de', 'family': 'DM Mono', 'size': 10},
            'bgcolor': 'rgba(114,230,222,.3)',
            'bordercolor': '#72e6de'
        }]
    )

def cinematic_orbit_figure(mu, lagrange_points, trajectory_rotating=None, time_values=None,
                            selected_point=None, primary_names=("Primary 1", "Primary 2"),
                            body_masses=(1.0, 0.0123)):
    """Inertial-frame playback where the complete system visibly revolves."""
    fig = go.Figure()
    dark = '#080d1e'
    rng = np.random.default_rng(19)
    # Subtle, sparse starfield — tiny dots at very low opacity
    fig.add_trace(go.Scatter(
        x=rng.uniform(-1.5, 1.5, 220), y=rng.uniform(-1.5, 1.5, 220), mode='markers',
        marker={'size': rng.uniform(.4, 1.8, 220), 'color': '#cce0ff', 'opacity': rng.uniform(.04, .22, 220)},
        hoverinfo='skip', showlegend=False))
    add_map_click_grid(fig)
    theta_ring = np.linspace(0, 2 * np.pi, 180)
    for radius, color in ((mu, 'rgba(255,209,102,.22)'), (1 - mu, 'rgba(114,230,222,.26)')):
        fig.add_trace(go.Scatter(x=radius*np.cos(theta_ring), y=radius*np.sin(theta_ring), mode='lines',
            line={'color': color, 'width': 1, 'dash': 'dot'}, hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker={'symbol': 'cross', 'size': 9, 'color': 'rgba(224,237,255,.65)'}, hoverinfo='skip', showlegend=False))

    l_names = list(lagrange_points)
    l_base = np.array([lagrange_points[name] for name in l_names])
    p_base = np.array([[-mu, 0.0], [1 - mu, 0.0]])
    if time_values is not None and trajectory_rotating is not None and len(time_values) == len(trajectory_rotating):
        phase = 6 * np.pi * (time_values - time_values[0]) / max(time_values[-1] - time_values[0], 1e-9)
    else:
        phase = np.linspace(0.0, 2 * np.pi, 120)

    def rotate(points, angle):
        c, s = np.cos(angle), np.sin(angle)
        return np.column_stack((points[:, 0] * c - points[:, 1] * s, points[:, 0] * s + points[:, 1] * c))
    
    p0, l0 = rotate(p_base, phase[0]), rotate(l_base, phase[0])

    # Sizes from actual masses via log scale — equal masses give equal sizes
    m1, m2 = body_masses
    p1_raw = mass_to_size(m1)
    p2_raw = mass_to_size(m2)
    body_halo_trace = len(fig.data)
    fig.add_trace(go.Scatter(x=p0[:, 0], y=p0[:, 1], mode='markers',
        marker={'size': [p1_raw * 1.8, p2_raw * 1.8], 'color': 'rgba(255, 209, 102, .06)'},
        hoverinfo='skip', showlegend=False))
    body_trace = len(fig.data)
    fig.add_trace(go.Scatter(x=p0[:, 0], y=p0[:, 1], mode='markers+text', text=list(primary_names), textposition='bottom center',
        marker={'size': [p1_raw, p2_raw], 'color': ['#ffd166', '#72e6de'],
                    'line': {'color': 'rgba(240,248,255,.7)', 'width': 1.5}},
        textfont={'color': '#eaf1ff', 'family': 'DM Mono', 'size': 10},
        hovertemplate='%{text}<extra></extra>', showlegend=False))
    lag_trace = len(fig.data)
    fig.add_trace(go.Scatter(x=l0[:, 0], y=l0[:, 1], mode='markers+text', text=l_names, customdata=l_names, textposition='top center',
        marker={'symbol': 'diamond', 'size': 10, 'color': '#aa95ff', 'line': {'color': '#eeeaff', 'width': 1}}, textfont={'color': '#f0edff', 'family': 'DM Mono', 'size': 10}, hovertemplate='%{text} equilibrium point<extra></extra>', showlegend=False))
    target_index = l_names.index(selected_point) if selected_point in l_names else None
    target_trace = None
    if target_index is not None:
        target_trace = len(fig.data)
        fig.add_trace(go.Scatter(x=[l0[target_index, 0]], y=[l0[target_index, 1]], mode='markers', hoverinfo='skip', showlegend=False, marker={'symbol': 'circle-open', 'size': 27, 'color': '#72e6de', 'line': {'width': 1.5}}))
    dynamic_traces = [body_halo_trace, body_trace, lag_trace]
    if target_trace is not None:
        dynamic_traces.append(target_trace)

    if trajectory_rotating is not None and len(trajectory_rotating):
        path0 = rotate(trajectory_rotating[:1], phase[0])
        path_trace = len(fig.data)
        fig.add_trace(go.Scatter(x=path0[:, 0], y=path0[:, 1], mode='lines', line={'color': '#95f1ec', 'width': 2.5}, hoverinfo='skip', showlegend=False))
        probe_halo_trace = len(fig.data)
        fig.add_trace(go.Scatter(x=path0[:, 0], y=path0[:, 1], mode='markers', marker={'size': 20, 'color': 'rgba(114,230,222,.18)'}, hoverinfo='skip', showlegend=False))
        probe_trace = len(fig.data)
        fig.add_trace(go.Scatter(x=path0[:, 0], y=path0[:, 1], mode='markers', marker={'size': 7, 'color': '#f5ffff', 'line': {'color': '#72e6de', 'width': 2}}, hovertemplate='Live probe<extra></extra>', showlegend=False))
        dynamic_traces += [path_trace, probe_halo_trace, probe_trace]
        frame_indices = np.unique(np.linspace(0, len(trajectory_rotating)-1, min(140, len(trajectory_rotating))).astype(int))
        frames = []
        for i in frame_indices:
            bodies, lags = rotate(p_base, phase[i]), rotate(l_base, phase[i])
            history = np.array([rotate(trajectory_rotating[j:j+1], phase[j])[0] for j in range(max(0, i-42), i+1)])
            data = [go.Scatter(x=bodies[:,0], y=bodies[:,1]), go.Scatter(x=bodies[:,0], y=bodies[:,1]), go.Scatter(x=lags[:,0], y=lags[:,1])]
            if target_index is not None: data.append(go.Scatter(x=[lags[target_index,0]], y=[lags[target_index,1]]))
            data += [go.Scatter(x=history[:,0], y=history[:,1]), go.Scatter(x=[history[-1,0]], y=[history[-1,1]]), go.Scatter(x=[history[-1,0]], y=[history[-1,1]])]
            frames.append(go.Frame(name=str(i), data=data, traces=dynamic_traces))
        fig.frames = frames
    else:
        frames = []
        for idx, angle in enumerate(phase):
            bodies, lags = rotate(p_base, angle), rotate(l_base, angle)
            data = [
                go.Scatter(x=bodies[:, 0], y=bodies[:, 1]),
                go.Scatter(x=bodies[:, 0], y=bodies[:, 1]),
                go.Scatter(x=lags[:, 0], y=lags[:, 1]),
            ]
            if target_index is not None:
                data.append(go.Scatter(x=[lags[target_index, 0]], y=[lags[target_index, 1]]))
            frames.append(go.Frame(name=str(idx), data=data, traces=dynamic_traces))
        fig.frames = frames

    fig.update_layout(plot_bgcolor=dark, paper_bgcolor=dark, margin={'l': 12,'r': 12,'t': 12,'b': 12}, showlegend=False,
        hoverlabel={'bgcolor': '#132142', 'bordercolor': '#72e6de', 'font': {'color': '#eff8ff', 'family': 'DM Mono', 'size': 11}},
        xaxis={'range': [-1.5,1.5], 'showgrid': True, 'gridcolor': 'rgba(155,181,240,.055)', 'showticklabels': False, 'zeroline': False, 'scaleanchor': 'y'},
        yaxis={'range': [-1.5,1.5], 'showgrid': True, 'gridcolor': 'rgba(155,181,240,.055)', 'showticklabels': False, 'zeroline': False})
    add_playback_controls(fig)
    return fig


def potential_terrain_figure(mu, lagrange_points, trajectory_rotating=None,
                             selected_point=None, primary_names=("Primary 1", "Primary 2")):
    """A manipulable 3D energy landscape for the same rotating-frame field."""
    grid = np.linspace(-1.45, 1.45, 90)
    x_grid, y_grid = np.meshgrid(grid, grid)
    z_raw = physics.effective_potential(x_grid, y_grid, mu)
    z_grid = np.clip(z_raw, 0, 4.2)
    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=x_grid, y=y_grid, z=z_grid, colorscale=[[0, '#0a1535'], [.35, '#17486a'], [.65, '#6a55a6'], [1, '#8de6d7']],
        cmin=0, cmax=4.2, opacity=.92, showscale=False,
        contours={'z': {'show': True, 'usecolormap': False, 'color': 'rgba(212,230,255,.2)', 'width': 1, 'highlight': False}},
        hovertemplate='x %{x:.3f}<br>y %{y:.3f}<br>potential %{z:.3f}<extra></extra>'
    ))
    primary_x = [-mu, 1 - mu]
    primary_z = [min(float(physics.effective_potential(x, 0, mu)), 4.2) + .08 for x in primary_x]
    fig.add_trace(go.Scatter3d(
        x=primary_x, y=[0, 0], z=primary_z, mode='markers+text', text=list(primary_names), textposition='top center',
        marker={'size': [26, 17], 'color': ['#ffd166', '#72e6de'], 'line': {'color': '#f0f7ff', 'width': 1}},
        textfont={'color': '#e7efff', 'size': 10, 'family': 'DM Mono'}, hovertemplate='%{text}<extra></extra>', showlegend=False
    ))
    names, xs, ys = zip(*[(name, point[0], point[1]) for name, point in lagrange_points.items()])
    zs = [min(float(physics.effective_potential(x, y, mu)), 4.2) + .025 for x, y in zip(xs, ys)]
    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs, mode='markers+text', text=names, textposition='top center', customdata=names,
        marker={'symbol': 'diamond', 'size': 6, 'color': '#af9aff', 'line': {'color': '#efeaff', 'width': 1}},
        textfont={'color': '#f3f0ff', 'size': 10, 'family': 'DM Mono'},
        hovertemplate='%{text} equilibrium point<extra></extra>', showlegend=False
    ))
    if selected_point in lagrange_points:
        x, y = lagrange_points[selected_point]
        z = min(float(physics.effective_potential(x, y, mu)), 4.2) + .05
        fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z], mode='markers', hoverinfo='skip', showlegend=False,
                                   marker={'symbol': 'circle-open', 'size': 11, 'color': '#72e6de', 'line': {'width': 2}}))
    if trajectory_rotating is not None and len(trajectory_rotating):
        path_z = np.clip(physics.effective_potential(trajectory_rotating[:, 0], trajectory_rotating[:, 1], mu), 0, 4.2) + .04
        fig.add_trace(go.Scatter3d(x=trajectory_rotating[:, 0], y=trajectory_rotating[:, 1], z=path_z,
                                   mode='lines', line={'color': '#9cefff', 'width': 4}, opacity=.75, hoverinfo='skip', showlegend=False))
        fig.add_trace(go.Scatter3d(x=[trajectory_rotating[0, 0]], y=[trajectory_rotating[0, 1]], z=[path_z[0]],
                                   mode='markers', marker={'size': 7, 'color': '#f4ffff', 'line': {'color': '#72e6de', 'width': 2}},
                                   hovertemplate='Live probe<extra></extra>', showlegend=False))
        frame_indices = np.unique(np.linspace(0, len(trajectory_rotating) - 1, min(120, len(trajectory_rotating))).astype(int))
        fig.frames = [go.Frame(name=str(i), data=[go.Scatter3d(x=[trajectory_rotating[i, 0]], y=[trajectory_rotating[i, 1]], z=[path_z[i]])], traces=[len(fig.data) - 1]) for i in frame_indices]
    fig.update_layout(
        paper_bgcolor='#080d1e', margin={'l': 0, 'r': 0, 't': 0, 'b': 0}, showlegend=False,
        scene={
            'bgcolor': '#080d1e',
            'xaxis': {'showbackground': False, 'showgrid': True, 'gridcolor': 'rgba(150,180,240,.12)', 'showticklabels': False, 'title': ''},
            'yaxis': {'showbackground': False, 'showgrid': True, 'gridcolor': 'rgba(150,180,240,.12)', 'showticklabels': False, 'title': ''},
            'zaxis': {'showbackground': False, 'showgrid': True, 'gridcolor': 'rgba(150,180,240,.10)', 'showticklabels': False, 'title': ''},
            'camera': {'eye': {'x': 1.55, 'y': -1.65, 'z': .95}}, 'aspectmode': 'cube'
        }
    )
    if trajectory_rotating is not None and len(trajectory_rotating) > 1:
        fig.update_layout(updatemenus=[{'type': 'buttons', 'direction': 'left', 'x': .02, 'y': .02, 'xanchor': 'left', 'yanchor': 'bottom',
            'bgcolor': 'rgba(13,24,52,.88)', 'bordercolor': 'rgba(114,230,222,.4)', 'borderwidth': 1, 'showactive': False, 'font': {'color': '#72e6de', 'family': 'DM Mono', 'size': 11},
            'buttons': [{'label': '▶', 'method': 'animate', 'args': [None, {"frame":{"duration":55,"redraw":True},"transition":{"duration":0},"fromcurrent":True}]}, {'label': 'Ⅱ', 'method': 'animate', 'args': [[None], {"frame":{"duration":0},"mode":"immediate"}]}]}])
    return fig

def system_figure(mu, lagrange_points: dict, trajectory_rotating: np.ndarray = None,
                   selected_point: str | None = None, primary_names: tuple = ("Primary 1", "Primary 2"),
                   view_mode: str = "Orbital plane", time_values: np.ndarray = None,
                   show_lagrange_points: bool = True,
                   body_masses: tuple = (1.0, 0.0123)) -> go.Figure:
    """
    Build a dark-themed 2D figure showing, in the rotating frame:
    - primary 1 at (-mu, 0) as a marker, size scaled by (1-mu), color e.g. '#ffd166'
    - primary 2 at (1-mu, 0) as a marker, size scaled by mu, color e.g. '#5eead4'
    - barycenter at (0,0) as a small '+' marker
    - each Lagrange point from lagrange_points dict as a diamond marker,
      labeled with its name (L1..L5), color '#a78bfa'
    - if trajectory_rotating is not None (shape (N,2)): plot it as a line
      with a color gradient / fading opacity from start to end, plus a
      bright marker at the final point representing the satellite's current
      position
    - dark background: plot_bgcolor and paper_bgcolor set to a dark navy
      (e.g. '#0a0e1a'), gridlines subdued, equal aspect ratio (fig.update_yaxes
      with scaleanchor='x')
    - no title inside the figure (title will be handled by Streamlit later)
    Return the Figure object. Do not call fig.show() — just return it.
    """
    if view_mode == "3D potential terrain":
        return potential_terrain_figure(mu, lagrange_points, trajectory_rotating, selected_point, primary_names)
    if view_mode == "Cinematic orbit":
        return cinematic_orbit_figure(mu, lagrange_points, trajectory_rotating, time_values,
                                     selected_point, primary_names, body_masses=body_masses)

    fig = go.Figure()

    dark_navy = '#080d1e'

    # Fine orbital guide rings establish scale and make the rotating frame feel
    # like an instrument rather than a plain scatter plot.
    for radius, opacity in ((0.25, .10), (.5, .10), (.75, .08), (1.0, .12), (1.25, .06)):
        fig.add_shape(
            type='circle', xref='x', yref='y', x0=-radius, y0=-radius, x1=radius, y1=radius,
            line={'color': f'rgba(114,230,222,{opacity})', 'width': 1, 'dash': 'dot'}, layer='below'
        )
    fig.add_shape(type='line', x0=-1.5, y0=0, x1=1.5, y1=0,
                  line={'color': 'rgba(152,174,229,.15)', 'width': 1, 'dash': 'dot'}, layer='below')
    
    # Sparse, small, low-opacity starfield that reads as deep space
    np.random.seed(42)
    sx = np.random.uniform(-1.5, 1.5, 200)
    sy = np.random.uniform(-1.5, 1.5, 200)
    fig.add_trace(go.Scatter(
        x=sx, y=sy, mode='markers',
        marker={'size': np.random.uniform(.4, 1.6, 200), 'color': '#cce0ff', 'opacity': np.random.uniform(.04, .22, 200)},
        hoverinfo='none', name='Starfield'
    ))
    add_map_click_grid(fig)

    # The L4/L5 triangle is a quick visual read of the equilateral geometry.
    if show_lagrange_points:
        l4 = lagrange_points.get('L4')
        l5 = lagrange_points.get('L5')
        if l4 and l5:
            fig.add_trace(go.Scatter(
                x=[-mu, 1.0 - mu, l4[0], -mu, None, 1.0 - mu, l5[0], -mu],
                y=[0, 0, l4[1], 0, None, 0, l5[1], 0], mode='lines',
                line={'color': 'rgba(168,149,255,.20)', 'width': 1, 'dash': 'dot'},
                hoverinfo='skip', showlegend=False
            ))

    # Barycenter
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers',
        marker={'symbol': 'cross', 'color': 'rgba(255,255,255,0.4)', 'size': 8},
        name="Barycenter",
        hoverinfo='none'
    ))
    
    if show_lagrange_points:
        # Log-scale sizes from actual masses — equal masses = equal sizes
        m1_mass, m2_mass = body_masses
        p1_size = mass_to_size(m1_mass)
        p2_size = mass_to_size(m2_mass)

        # Lagrange Points
        l_names = []
        l_xs = []
        l_ys = []
        for name, (x, y) in lagrange_points.items():
            l_names.append(name)
            l_xs.append(x)
            l_ys.append(y)
            
        # Lagrange Points Glow
        fig.add_trace(go.Scatter(
            x=l_xs, y=l_ys,
            mode='markers',
            marker={'symbol': 'circle', 'size': 18, 'color': 'rgba(167, 139, 250, 0.15)'},
            hoverinfo='none', showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=l_xs, y=l_ys,
            mode='markers+text',
            marker={
                'symbol': 'diamond', 
                'size': 6.5, 
                'color': '#a78bfa',
                'line': {'width': 2, 'color': 'rgba(167, 139, 250, 0.7)'}
            },
            text=l_names,
            customdata=l_names,
            textposition='top center',
            textfont={'color': 'white', 'size': 9, 'family': 'Courier New'},
            name="Lagrange Points",
            hovertemplate='%{text} equilibrium point<br>x: %{x:.4f}<br>y: %{y:.4f}<extra></extra>'
        ))

        # The selected target receives its own luminous targeting reticle.
        if selected_point in lagrange_points:
            target_x, target_y = lagrange_points[selected_point]
            fig.add_trace(go.Scatter(
                x=[target_x], y=[target_y], mode='markers', hoverinfo='skip', showlegend=False,
                marker={'symbol': 'circle-open', 'size': 24, 'color': '#72e6de', 'line': {'width': 1.5, 'color': '#72e6de'}}
            ))

        # Primary 1 — multi-layer glow (3 concentric halos for smooth falloff)
        for glow_scale, glow_opacity in [(2.8, .05), (2.0, .09), (1.55, .13)]:
            fig.add_trace(go.Scatter(
                x=[-mu], y=[0], mode='markers', hoverinfo='none', showlegend=False,
                marker={'size': p1_size * glow_scale, 'color': f'rgba(255,209,102,{glow_opacity})'}
            ))
        fig.add_trace(go.Scatter(
            x=[-mu], y=[0], mode='markers+text',
            text=[primary_names[0]], textposition='bottom center',
            textfont={'color': '#ffd166', 'size': 12, 'family': 'DM Mono'},
            marker={'size': p1_size, 'color': '#ffd166', 'line': {'width': 2, 'color': 'rgba(255,232,140,.75)'}},
            name=primary_names[0], hovertemplate=f'{primary_names[0]}<br>x: %{{x:.4f}}<extra></extra>'
        ))

        # Primary 2 — multi-layer glow
        for glow_scale, glow_opacity in [(2.8, .05), (2.0, .09), (1.55, .13)]:
            fig.add_trace(go.Scatter(
                x=[1.0 - mu], y=[0], mode='markers', hoverinfo='none', showlegend=False,
                marker={'size': p2_size * glow_scale, 'color': f'rgba(94,234,212,{glow_opacity})'}
            ))
        fig.add_trace(go.Scatter(
            x=[1.0 - mu], y=[0], mode='markers+text',
            text=[primary_names[1]], textposition='bottom center',
            textfont={'color': '#5eead4', 'size': 12, 'family': 'DM Mono'},
            marker={'size': p2_size, 'color': '#5eead4', 'line': {'width': 2, 'color': 'rgba(160,240,235,.75)'}},
            name=primary_names[1], hovertemplate=f'{primary_names[1]}<br>x: %{{x:.4f}}<extra></extra>'
        ))    
    # Trajectory and playback. Plotly frames update only the probe marker, leaving
    # the calculated path visible as a quiet reference beneath it.
    if trajectory_rotating is not None and len(trajectory_rotating) > 0:
        fig.add_trace(go.Scatter(
            x=trajectory_rotating[:, 0],
            y=trajectory_rotating[:, 1],
            mode='lines',
            line={'color': 'rgba(152, 232, 255, .72)', 'width': 1.7},
            opacity=0.7,
            name="Trajectory"
        ))
        # This short, bright segment travels with the probe to sell the motion.
        fig.add_trace(go.Scatter(
            x=[trajectory_rotating[0, 0]], y=[trajectory_rotating[0, 1]], mode='lines',
            line={'color': 'rgba(114,230,222,.95)', 'width': 3}, hoverinfo='skip', showlegend=False
        ))
        # A soft halo makes the active satellite easy to find without obscuring the map.
        fig.add_trace(go.Scatter(
            x=[trajectory_rotating[0, 0]], y=[trajectory_rotating[0, 1]],
            mode='markers', marker={'size': 18, 'color': 'rgba(114, 230, 222, .14)'},
            hoverinfo='skip', showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=[trajectory_rotating[0, 0]],
            y=[trajectory_rotating[0, 1]],
            mode='markers',
            marker={'size': 7, 'color': '#ecfbff', 'line': {'color': '#72e6de', 'width': 1.8}},
            name="Satellite", hovertemplate='Probe<br>x: %{x:.4f}<br>y: %{y:.4f}<extra></extra>'
        ))

        # Keep animation lightweight even when integration returns many samples.
        frame_indices = np.unique(np.linspace(0, len(trajectory_rotating) - 1, min(120, len(trajectory_rotating))).astype(int))
        fig.frames = [
            go.Frame(
                name=str(i),
                data=[
                    go.Scatter(x=trajectory_rotating[max(0, i - 18):i + 1, 0], y=trajectory_rotating[max(0, i - 18):i + 1, 1]),
                    go.Scatter(x=[trajectory_rotating[i, 0]], y=[trajectory_rotating[i, 1]]),
                    go.Scatter(x=[trajectory_rotating[i, 0]], y=[trajectory_rotating[i, 1]])
                ],
                traces=[len(fig.data) - 3, len(fig.data) - 2, len(fig.data) - 1]
            )
            for i in frame_indices
        ]

    fig.update_layout(
        plot_bgcolor=dark_navy,
        paper_bgcolor=dark_navy,
        font={'color': 'white'},
        showlegend=False,
        margin={'l': 14, 'r': 14, 't': 14, 'b': 14},
        hoverlabel={'bgcolor': '#131f40', 'bordercolor': '#72e6de', 'font': {'color': '#edf7ff', 'family': 'DM Mono', 'size': 11}},
        xaxis={
            'scaleanchor': 'y',
            'scaleratio': 1,
            'showgrid': True,
            'gridcolor': 'rgba(155,181,240,.055)',
            'zeroline': False, 'showticklabels': False, 'ticks': '', 'range': [-1.5, 1.5], 'fixedrange': False
        },
        yaxis={
            'showgrid': True,
            'gridcolor': 'rgba(155,181,240,.055)',
            'zeroline': False, 'showticklabels': False, 'ticks': '', 'range': [-1.5, 1.5], 'fixedrange': False
        }
    )

    add_playback_controls(fig)
    
    return fig

if __name__ == "__main__":
    test_mu = 0.0121
    l_points = physics.all_lagrange_points(test_mu)
    fig = system_figure(test_mu, l_points)
    fig.write_html("test_viz.html")
    print("test_viz.html created successfully.")
