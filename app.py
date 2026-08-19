# pylint: disable=missing-docstring, redefined-outer-name, invalid-name, line-too-long, too-many-arguments, too-many-positional-arguments, broad-exception-caught, import-error
import numpy as np  # type: ignore
import streamlit as st  # type: ignore

import frames
import manim_viz
import physics
import rebound_sim
import viz

st.set_page_config(
    layout="wide",
    page_title="Celestia · Orbital Lab",
    page_icon="✦",
    initial_sidebar_state="expanded",
)


@st.dialog("Export Cinematic Video", width="large")
def export_video_dialog(mu, sat_rotating, actual_name1, actual_name2, m1_val, m2_val):
    st.write("Rendering a high-quality cinematic animation. Please wait...")
    if sat_rotating is not None:
        with st.spinner("Manim is rendering the simulation..."):
            video_path = manim_viz.render_trajectory(
                mu,
                sat_rotating,
                "orbital_simulation",
                actual_name1,
                actual_name2,
                m1_val,
                m2_val,
            )
            st.session_state.manim_video_path = video_path
        if st.session_state.get("manim_video_path"):
            st.video(st.session_state.manim_video_path)
    else:
        st.error("No trajectory available to render.")


CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root { --ink: #eaf0ff; --muted: #8190af; --panel: rgba(17, 27, 52, .72); --line: rgba(164, 185, 255, .13); --cyan: #72e6de; --violet: #9e8cff; }
    #splash-screen {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at center, #0e172c 0%, #040812 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: fadeOut 0.8s ease-in-out 1.2s forwards;
        pointer-events: none;
    }
    .loader-container {
        position: relative;
        width: 140px;
        height: 140px;
        margin-bottom: 2.5rem;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .loader-orbit {
        position: absolute;
        border-radius: 50%;
        border: 2px solid transparent;
        box-sizing: border-box;
    }
    .loader-orbit-1 {
        width: 100%;
        height: 100%;
        border-top-color: rgba(114, 230, 222, 0.9);
        border-right-color: rgba(114, 230, 222, 0.3);
        border-bottom-color: rgba(114, 230, 222, 0.1);
        animation: spin 2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
    }
    .loader-orbit-2 {
        width: 75%;
        height: 75%;
        border-top-color: rgba(158, 140, 255, 0.9);
        border-left-color: rgba(158, 140, 255, 0.3);
        border-bottom-color: rgba(158, 140, 255, 0.1);
        animation: spin-reverse 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
    }
    .loader-orbit-3 {
        width: 50%;
        height: 50%;
        border-top-color: rgba(255, 255, 255, 0.7);
        border-right-color: rgba(255, 255, 255, 0.2);
        animation: spin 1s linear infinite;
    }
    .loader-core {
        width: 15%;
        height: 15%;
        background: #72e6de;
        border-radius: 50%;
        box-shadow: 0 0 15px #72e6de, 0 0 35px #72e6de, 0 0 60px rgba(158, 140, 255, 0.6);
        animation: core-pulse 1.2s ease-in-out infinite alternate;
    }
    #splash-screen h1 {
        color: #ffffff;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(2.8rem, 8vw, 5rem);
        letter-spacing: 0.35em;
        text-shadow: 0 0 40px rgba(114, 230, 222, 0.3);
        margin: 0;
        animation: fadeInUp 0.8s ease-out forwards;
        opacity: 0;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff, #9e8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    #splash-screen p {
        color: #8190af;
        font-size: 1.1rem;
        font-family: 'DM Mono', monospace;
        margin-top: 1.5rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        opacity: 0;
        animation: fadeInUp 0.8s ease-out 0.3s forwards;
    }
    .loading-bar-container {
        width: 250px;
        height: 2px;
        background: rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
        border-radius: 2px;
        overflow: hidden;
        opacity: 0;
        animation: fadeInUp 0.8s ease-out 0.4s forwards;
    }
    .loading-bar {
        height: 100%;
        background: #72e6de;
        width: 0%;
        box-shadow: 0 0 10px #72e6de;
        animation: loadingBar 0.8s cubic-bezier(0.65, 0, 0.35, 1) 0.4s forwards;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes spin-reverse { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }
    @keyframes core-pulse { 0% { transform: scale(0.7); opacity: 0.6; } 100% { transform: scale(1.3); opacity: 1; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(25px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes loadingBar { 0% { width: 0%; } 50% { width: 70%; } 100% { width: 100%; } }
    @keyframes fadeOut { to { opacity: 0; visibility: hidden; backdrop-filter: blur(0px); -webkit-backdrop-filter: blur(0px); } }

    /* Ultra nice cinematic video modal styles */
    [data-testid="stDialog"] { 
        width: 85vw !important; 
        max-width: 1200px !important;
        margin: auto !important;
        border-radius: 20px !important; 
        background: #040812 !important; 
        border: 1px solid rgba(114,230,222,.3) !important; 
        box-shadow: 0 20px 80px rgba(0,0,0,0.8) !important;
    }
    [data-testid="stDialog"] > div {
        background: transparent !important;
    }
    [data-testid="stDialog"] [data-testid="stVideo"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    [data-testid="stDialog"] video { 
        width: 100% !important; 
        max-width: 1280px !important;
        max-height: 75vh !important;
        border-radius: 12px !important; 
        margin: 0 auto !important; 
        display: block !important; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.6) !important; 
    }

    .stApp {
        color: var(--ink);
        font-family: 'Manrope', sans-serif;
        background: radial-gradient(ellipse 85% 55% at 75% -5%, rgba(82, 72, 180, .20), transparent 70%), radial-gradient(ellipse 55% 40% at 25% 30%, rgba(15, 153, 171, .10), transparent 70%), #070b18;
    }
    /* Remove Streamlit's default white toolbar elements and header */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
    
    /* Hide the sidebar collapse button so mission control is always visible */
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    
    [data-testid="stAppViewContainer"] > .main { padding-top: 0; }
    .stApp:before { content:""; position:fixed; inset:0; pointer-events:none; opacity:.28; background-image:linear-gradient(rgba(144,165,255,.035) 1px, transparent 1px),linear-gradient(90deg, rgba(144,165,255,.035) 1px, transparent 1px); background-size:42px 42px; mask-image:linear-gradient(to bottom, black, transparent 75%); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(12, 18, 38, .98), rgba(7, 11, 24, .97));
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: .55rem; }
    [data-testid="stSidebar"] .stVerticalBlock { gap: .8rem; }
    .block-container { max-width: 1560px; padding: 2.2rem 2.65rem 2.8rem; }
    h1, h2, h3 { color: var(--ink) !important; font-family:'Manrope', sans-serif !important; }
    h2 { font-size: 1.13rem !important; letter-spacing: -.02em; }
    p, label, [data-testid="stCaptionContainer"] { color: var(--muted); }
    .sidebar-brand { padding: .75rem .15rem 1.2rem; }
    .sidebar-brand__eyebrow, .eyebrow { color: var(--cyan); font-family:'DM Mono', monospace; font-size:.67rem; text-transform:uppercase; letter-spacing:.14em; }
    .sidebar-brand__title { margin:.35rem 0 .28rem; color:var(--ink); font-size:1.55rem; letter-spacing:-.07em; font-weight:800; }
    .sidebar-brand__sub { color:var(--muted); font-size:.75rem; line-height:1.45; }
    .sidebar-rule { height:1px; margin:.35rem 0 .45rem; background:linear-gradient(90deg,var(--cyan),transparent); opacity:.55; }
    .control-card__head { display:flex; align-items:flex-start; justify-content:space-between; gap:.7rem; margin:.05rem 0 .8rem; }
    .control-card__title { color:var(--ink); font-size:.93rem; font-weight:800; letter-spacing:-.025em; }
    .control-card__sub { margin-top:.18rem; color:#8291b0; font-size:.66rem; line-height:1.45; }
    .control-card__tag { padding:.24rem .38rem; border:1px solid rgba(114,230,222,.24); border-radius:5px; color:var(--cyan); font-family:'DM Mono'; font-size:.55rem; letter-spacing:.08em; }
    .control-divider { height:1px; margin:.75rem 0; background:linear-gradient(90deg,rgba(155,177,248,.19),transparent); }
    .slider-caption { margin:.6rem 0 -.35rem; color:#b9c5dd; font-family:'DM Mono'; font-size:.59rem; letter-spacing:.1em; text-transform:uppercase; }
    [data-testid="stSidebar"] [data-testid="stToggle"] { padding:.45rem .15rem; border-bottom:1px solid rgba(155,177,248,.1); }
    [data-testid="stSidebar"] [data-testid="stToggle"] label { color:#b9c6df !important; font-size:.75rem; font-weight:600; }
    .hero { position:relative; overflow:hidden; min-height:160px; padding:1.9rem 2rem; border:1px solid var(--line); border-radius:22px; background:linear-gradient(120deg, rgba(19,34,70,.88), rgba(17,24,51,.62)); box-shadow:0 20px 55px rgba(0,0,0,.19); }
    .hero:after { content:""; position:absolute; width:320px; height:320px; right:-85px; top:-190px; border:1px solid rgba(114,230,222,.25); border-radius:50%; box-shadow:0 0 0 36px rgba(114,230,222,.04),0 0 0 73px rgba(158,140,255,.035); }
    .hero__title { position:relative; z-index:1; margin:.45rem 0; font-size:clamp(2rem,3.4vw,3.2rem); line-height:1; letter-spacing:-.075em; font-weight:800; color:var(--ink); }
    .hero__copy { position:relative; z-index:1; max-width:550px; color:#9eabc6; font-size:.91rem; line-height:1.55; }
    .hero__status { position:absolute; z-index:1; top:1.6rem; right:1.7rem; display:flex; align-items:center; gap:.45rem; color:#b7c3dd; font-family:'DM Mono'; font-size:.65rem; letter-spacing:.08em; }
    .pulse-dot { height:7px; width:7px; border-radius:50%; background:var(--cyan); box-shadow:0 0 0 0 rgba(114,230,222,.65); animation:orbital-pulse 1.9s infinite; }
    @keyframes orbital-pulse { 70% { box-shadow:0 0 0 8px rgba(114,230,222,0); } 100% { box-shadow:0 0 0 0 rgba(114,230,222,0); } }
    .section-head { display:flex; align-items:center; justify-content:space-between; margin:1.55rem 0 .65rem; }
    .section-head__title { color:var(--ink); font-weight:700; letter-spacing:-.03em; }
    .section-head__detail { color:var(--muted); font-family:'DM Mono'; font-size:.67rem; text-transform:uppercase; letter-spacing:.1em; }
    .field-cue { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:-.1rem 0 .7rem; padding:.62rem .75rem; border:1px solid rgba(155,177,248,.12); border-radius:12px; background:rgba(8,15,34,.52); }
    .field-cue__copy { color:#91a0bd; font-size:.7rem; }
    .field-cue__legend { display:flex; align-items:center; flex-wrap:wrap; justify-content:flex-end; gap:.8rem; color:#b9c6df; font-family:'DM Mono'; font-size:.61rem; letter-spacing:.03em; }
    .legend-dot { display:inline-block; width:7px; height:7px; margin-right:.28rem; border-radius:50%; vertical-align:middle; }
    .legend-diamond { color:#a895ff; font-size:.9rem; vertical-align:-.08rem; }
    .system-summary { display:flex; gap:.5rem; padding:.7rem .78rem; margin:.15rem 0 .35rem; border:1px solid rgba(114,230,222,.16); border-radius:11px; background:rgba(114,230,222,.045); color:#b5c8d5; font-size:.72rem; line-height:1.4; }
    .system-summary strong { color:var(--cyan); font-family:'DM Mono'; font-weight:500; }
    .control-label { color:#b6c3dc; font-size:.75rem; font-weight:700; letter-spacing:.01em; }
    [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--line) !important; border-radius:16px !important; background:linear-gradient(145deg, rgba(29,42,78,.46), rgba(12,18,37,.52)) !important; box-shadow:0 16px 38px rgba(0,0,0,.15); }
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] { border-radius:14px !important; background:linear-gradient(145deg, rgba(25,37,69,.64), rgba(10,15,31,.58)) !important; }
    [data-testid="stMetric"] { padding:.45rem .15rem; }
    [data-testid="stMetricLabel"] { color:var(--muted) !important; font-size:.68rem !important; font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:.08em; }
    [data-testid="stMetricValue"] { font-family:'DM Mono',monospace; color:var(--violet) !important; font-size:1.25rem !important; font-weight:500; }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div { background:rgba(4,8,20,.52) !important; border-color:rgba(165,188,255,.16) !important; border-radius:10px !important; color:var(--ink) !important; }
    [data-baseweb="select"] > div:hover, [data-baseweb="input"] > div:hover { border-color:rgba(114,230,222,.5) !important; }
    [data-testid="stSlider"] [data-testid="stThumbValue"] { color:var(--cyan); font-family:'DM Mono'; font-size:.68rem; }
    [data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div { background:var(--cyan) !important; }
    [data-testid="stRadio"] { gap:.25rem; }
    [data-testid="stRadio"] label { border-radius:9px; transition:all .2s ease; }
    [data-testid="stRadio"] label:hover { background:rgba(114,230,222,.08); }
    .stButton>button, [data-testid="baseButton-secondary"] { min-height:2.8rem; border-radius:11px; background:rgba(37,51,90,.68) !important; border:1px solid rgba(164,185,255,.25) !important; color:#dce8ff !important; font-family:'Manrope',sans-serif; font-size:.69rem; font-weight:800; letter-spacing:.055em; text-transform:uppercase; transition:all .2s ease; }
    .stButton>button[kind="primary"], [data-testid="baseButton-primary"] { background:linear-gradient(135deg, #74e7dd, #8392ff) !important; color:#07101f !important; border:1px solid transparent !important; box-shadow:0 10px 25px rgba(96,203,221,.22); }
    .stButton>button:hover, [data-testid="baseButton-secondary"]:hover, [data-testid="baseButton-primary"]:hover { transform:translateY(-2px); border-color:rgba(114,230,222,.72) !important; box-shadow:0 13px 28px rgba(96,203,221,.25); }
    .playback-panel { display:flex; gap:.6rem; margin-top:.6rem; align-items:center; }
    .speed-pill { display:inline-flex; align-items:center; justify-content:center; min-width:4.2rem; padding:.45rem .5rem; border-radius:10px; background:rgba(19, 29, 50, .9); border:1px solid rgba(150,173,255,.18); color:#dceaff; font-family:'DM Mono'; font-size:.72rem; font-weight:600; }
    .stability-badge { display:inline-flex; align-items:center; gap:.45rem; padding:.45rem .75rem; border-radius:999px; font-family:'DM Mono'; font-size:.66rem; letter-spacing:.06em; margin:0 0 .2rem; }
    .badge-stable { background:rgba(61,220,155,.1); color:#68e6b2; border:1px solid rgba(61,220,155,.28); }
    .badge-unstable { background:rgba(255,131,142,.10); color:#ff9ba6; border:1px solid rgba(255,131,142,.28); }
    [data-testid="stPlotlyChart"] { border:1px solid var(--line); border-radius:18px; overflow:hidden; background:#080d1e; box-shadow:0 18px 50px rgba(0,0,0,.18); }
    hr { border-color:var(--line) !important; margin:1.6rem 0 !important; }
    @media (max-width: 800px) { .block-container { padding:1.25rem 1rem 2rem; } .hero { min-height:145px; padding:1.5rem; } .hero__status { position:relative; top:auto; right:auto; margin-top:1rem; } }
    [data-testid="stSidebarContent"] { padding-top: 1.5rem !important; }
    [data-testid="stSidebarHeader"] { padding-top: 0 !important; display: none !important; }
</style>
"""
st.html(CUSTOM_CSS)

st.html("""
<div id="splash-screen">
    <div class="loader-container">
        <div class="loader-orbit loader-orbit-1"></div>
        <div class="loader-orbit loader-orbit-2"></div>
        <div class="loader-orbit loader-orbit-3"></div>
        <div class="loader-core"></div>
    </div>
    <h1>CELESTIA</h1>
    <p>Orbital Dynamics Laboratory</p>
    <div class="loading-bar-container"><div class="loading-bar"></div></div>
</div>
""")

SOLAR_SYSTEM = {
    "Sun": 332946.0,
    "Mercury": 0.0553,
    "Venus": 0.815,
    "Earth": 1.0,
    "Moon": 0.0123,
    "Mars": 0.107,
    "Jupiter": 317.83,
    "Saturn": 95.16,
    "Uranus": 14.54,
    "Neptune": 17.15,
    "Pluto": 0.0022,
    "Custom": None,
}

# Initialize session state
if "body1" not in st.session_state:
    st.session_state.body1 = "Earth"
    st.session_state.body2 = "Moon"
    st.session_state.m1_custom = 1.0
    st.session_state.m2_custom = 0.0123
    st.session_state.separation = 1.0
    st.session_state.selected_point = None
    st.session_state.perturb_radial = 0.0
    st.session_state.perturb_tangential = 0.0
    st.session_state.perturb_velocity = 0.0
    st.session_state.trajectory = None
    st.session_state.trajectory_times = None
    st.session_state.map_body_positions = []
    st.session_state.map_placement_notice = False
    st.session_state.last_map_click = None
    st.session_state.manim_video_path = None
    st.session_state.is_rendering = False

st.html("""
<section class="hero">
  <div class="eyebrow">Restricted three-body problem · Live workspace</div>
  <div class="hero__title">Celestia <span style="color:#72e6de">·</span> Orbital Lab</div>
  <div class="hero__copy">Explore gravitational balance points, test a satellite's response, and play back its path in the rotating reference frame.</div>
  <div class="hero__status"><span class="pulse-dot"></span> SYSTEMS NOMINAL</div>
</section>
""")

# Sidebar
st.sidebar.html("""
<div class="sidebar-brand">
  <div class="sidebar-brand__eyebrow">Celestia / mission control</div>
  <div class="sidebar-brand__title">Configure mission</div>
  <div class="sidebar-brand__sub">Tune the two-body system, place a probe, then run a three-period forecast.</div>
</div>
<div class="sidebar-rule"></div>
""")
with st.sidebar.container(border=True):
    col1, col2 = st.columns([5, 1], vertical_alignment="center")
    with col1:
        st.html(
            '<div class="control-card__title" style="font-size: 1.3rem; margin-bottom: 0.5rem; font-weight: 700; color: #fff;">System parameters</div>'
        )
    with col2:
        if st.button(
            "↺",
            key="reset_sys",
            use_container_width=True,
            help="Reset system to Earth–Moon",
        ):
            st.session_state.body1 = "Earth"
            st.session_state.body2 = "Moon"
            st.session_state.m1_custom = 1.0
            st.session_state.m2_custom = 0.0123
            st.session_state.separation = 1.0
            st.rerun()
    st.caption("THE GRAVITATIONAL ENVIRONMENT")

    body1 = st.selectbox("Primary Body", list(SOLAR_SYSTEM.keys()), key="body1")
    if body1 == "Custom":
        m1_input = st.number_input(
            "Mass 1 (Earth Masses)", min_value=1e-6, format="%.4f", key="m1_custom"
        )
    else:
        m1_input = SOLAR_SYSTEM[body1]
        st.html(
            f'<div class="system-summary"><strong>M₁</strong><span>{m1_input:,.4g} Earth masses</span></div>'
        )

    body2 = st.selectbox("Secondary Body", list(SOLAR_SYSTEM.keys()), key="body2")
    if body2 == "Custom":
        m2_input = st.number_input(
            "Mass 2 (Earth Masses)", min_value=1e-6, format="%.6f", key="m2_custom"
        )
    else:
        m2_input = SOLAR_SYSTEM[body2]
        st.html(
            f'<div class="system-summary"><strong>M₂</strong><span>{m2_input:,.4g} Earth masses</span></div>'
        )

    # Enforce m1 >= m2 mathematically to avoid CR3BP solver issues where mu > 0.5
    m1_val = max(m1_input, m2_input)
    m2_val = min(m1_input, m2_input)

    if m1_input < m2_input:
        st.info(
            "Note: Secondary body is more massive. Masses have been mathematically swapped for the simulation (Primary is always the heaviest)."
        )
        actual_name1, actual_name2 = st.session_state.body2, st.session_state.body1
    else:
        actual_name1, actual_name2 = st.session_state.body1, st.session_state.body2

    separation = st.slider("Separation (AU)", 0.1, 5.0, st.session_state.separation)
    st.session_state.separation = separation

    if st.session_state.map_placement_notice:
        st.info(
            "Map placement active — custom bodies are selected and their separation comes from the two map clicks."
        )

    # (Reset button moved to header)

    # Compute mu
    is_stable = False
    try:
        mu = physics.mass_ratio(m1_val, m2_val)
        st.metric("Mass ratio μ", f"{mu:.6f}")
        is_stable = mu < 0.038521
    except ValueError as e:
        st.error(str(e))
        mu = None

if mu is not None:
    with st.sidebar.container(border=True):
        col1, col2 = st.columns([5, 1], vertical_alignment="center")
        with col1:
            st.html("""
            <div class="control-card__head">
              <div><div class="control-card__title">Satellite &amp; perturbation</div><div class="control-card__sub">Set the launch point and adjust its initial state.</div></div>
            </div>
            """)
        with col2:
            if st.button(
                "↺",
                key="reset_probe",
                use_container_width=True,
                help="Recenter probe and zero the perturbations",
            ):
                st.session_state.perturb_radial = 0.0
                st.session_state.perturb_tangential = 0.0
                st.session_state.perturb_velocity = 0.0
                st.rerun()
        st.html('<div class="slider-caption">Target equilibrium point</div>')
        selected_point = st.radio(
            "Select Lagrange Point",
            ["L1", "L2", "L3", "L4", "L5"],
            key="selected_point",
            index=None,
            horizontal=True,
        )

        if selected_point is None:
            st.error(
                "Please select a target equilibrium point first to start the simulation."
            )
        elif selected_point in ["L1", "L2", "L3"]:
            st.html(
                f'<div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.4); padding: 0.75rem 1rem; border-radius: 6px; color: #ff6b6b; font-size: 0.9rem; margin: 0.75rem 0; display: flex; align-items: center; gap: 0.5rem;"><span style="font-size: 1.1rem;">⚠</span> {selected_point} is an unstable saddle point</div>'
            )
        else:
            if is_stable:
                st.html(
                    f'<div style="background: rgba(94, 234, 212, 0.1); border: 1px solid rgba(94, 234, 212, 0.4); padding: 0.75rem 1rem; border-radius: 6px; color: #5eead4; font-size: 0.9rem; margin: 0.75rem 0; display: flex; align-items: center; gap: 0.5rem;"><span style="font-size: 1.1rem;">✓</span> {selected_point} region is stable</div>'
                )
            else:
                st.html(
                    f'<div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.4); padding: 0.75rem 1rem; border-radius: 6px; color: #ff6b6b; font-size: 0.9rem; margin: 0.75rem 0; display: flex; align-items: center; gap: 0.5rem;"><span style="font-size: 1.1rem;">⚠</span> {selected_point} region is unstable</div>'
                )

        st.html(
            '<div class="control-divider"></div><div class="slider-caption">Position trim</div>'
        )
        perturb_radial = st.slider(
            "Move in/out", -1.5, 1.5, key="perturb_radial", step=0.001
        )

        perturb_tangential = st.slider(
            "Move sideways", -1.5, 1.5, key="perturb_tangential", step=0.001
        )

        st.html('<div class="slider-caption">Velocity trim</div>')
        perturb_velocity = st.slider(
            "Nudge move", -1.0, 1.0, key="perturb_velocity", step=0.001
        )

        # (Reset button moved to header)

        st.html('<div class="control-divider"></div>')

        try:
            if selected_point is None:
                st.session_state.trajectory = None
                st.session_state.trajectory_times = None
                st.session_state.is_rendering = False
            else:
                all_points = physics.all_lagrange_points(mu)
                base_x, base_y = all_points[selected_point]
                start_x = base_x + perturb_radial
                start_y = base_y + perturb_tangential
                m_total = m1_val + m2_val
                omega = np.sqrt(1.0 * m_total / (separation**3))
                vx = -omega * start_y
                vy = omega * start_x
                speed = np.sqrt(vx**2 + vy**2)
                if speed > 1e-9:
                    vx += (vx / speed) * perturb_velocity
                    vy += (vy / speed) * perturb_velocity
                sim = rebound_sim.build_simulation(mu, m_total, separation)
                rebound_sim.add_satellite(sim, start_x, start_y, vx, vy)
                period = 2.0 * np.pi / omega
                t_end = 10.0 * period
                data = rebound_sim.run_and_record(sim, t_end, 800)
                sat_rotating = frames.to_rotating_frame(data["t"], data["sat"], omega)
                st.session_state.trajectory = sat_rotating
                st.session_state.trajectory_times = data["t"]

        except Exception:  # noqa: BLE001
            st.session_state.trajectory = None
            st.session_state.trajectory_times = None
            st.session_state.is_rendering = False

    with st.sidebar.container(border=True):
        st.html("""
        <div class="control-card__head">
          <div><div class="control-card__title">Display layers</div><div class="control-card__sub">Reveal the physical structure behind the trajectory.</div></div>
          <div class="control-card__tag">ANALYSIS</div>
        </div>
        """)
        st.markdown(
            """
            <div class="system-summary">
              Select a viewing mode for the simulation.
            </div>
            """,
            unsafe_allow_html=True,
        )
        view_mode_simple = st.radio(
            "Map mode",
            ["Cinematic", "2D Map", "3D Terrain"],
            horizontal=True,
            label_visibility="collapsed",
        )
        viz_view_mode_map = {
            "Cinematic": "Cinematic orbit",
            "2D Map": "Orbital plane",
            "3D Terrain": "3D potential terrain",
        }
        view_mode = viz_view_mode_map[view_mode_simple]

    # Main Area Plot
    all_points = physics.all_lagrange_points(mu)

    col_head, col_btn = st.columns([5, 1], vertical_alignment="bottom")
    with col_head:
        st.html("""
        <div class="section-head" style="margin-bottom:0;">
          <div><div class="eyebrow">Rotating reference frame</div><div class="section-head__title">Orbital field map</div></div>
        </div>
        """)
    with col_btn:
        if st.button("Export Video", use_container_width=True):
            export_video_dialog(
                mu,
                st.session_state.trajectory,
                actual_name1,
                actual_name2,
                m1_val,
                m2_val,
            )
    jacobi_val = None
    if st.session_state.trajectory is not None:
        start_x = st.session_state.trajectory[0, 0]
        start_y = st.session_state.trajectory[0, 1]
        jacobi_val = physics.jacobi_constant(
            mu, start_x, start_y, st.session_state.perturb_velocity, 0.0
        )

        # Stability Badge above the plot
        if selected_point is not None:
            base_pt = all_points[selected_point]
            stab_info = physics.stability(mu, base_pt)
            stab_class = stab_info["classification"]

            if stab_class == "stable":
                badge_html = f'<div class="stability-badge badge-stable">● {selected_point} · STABLE REGION</div>'
            else:
                badge_html = f'<div class="stability-badge badge-unstable">● {selected_point} · UNSTABLE SADDLE</div>'

            st.markdown(badge_html, unsafe_allow_html=True)

    st.html(f"""
    <div class="field-cue">
      <div class="field-cue__copy">Click on the orbital map to place custom bodies and calculate separation. Adjust parameters and click Render for a cinematic video.</div>
      <div class="field-cue__legend">
        <div><span class="legend-dot" style="background:#ffd166;"></span>{actual_name1}</div>
        <div><span class="legend-dot" style="background:#5eead4;"></span>{actual_name2}</div>
        <div><span class="legend-diamond">◆</span> Lagrange Points</div>
        <div><span class="legend-dot" style="background:#ecfbff; border:1px solid #72e6de; width:9px; height:9px; vertical-align:-.05rem;"></span> Satellite</div>
      </div>
    </div>
    """)

    fig = viz.system_figure(
        mu,
        all_points,
        trajectory_rotating=st.session_state.trajectory,
        selected_point=st.session_state.selected_point,
        primary_names=(actual_name1, actual_name2),
        view_mode=view_mode,
        time_values=st.session_state.trajectory_times,
        body_masses=(m1_val, m2_val),
    )

    event = st.plotly_chart(
        fig, key="orbital_map", on_select="rerun", selection_mode="points"
    )
    if event and event["selection"] and event["selection"]["points"]:
        pt = event["selection"]["points"][0]
        if "customdata" in pt and pt["customdata"][0] == "map":
            cx, cy = pt["customdata"][1], pt["customdata"][2]
            st.session_state.last_map_click = (cx, cy)

            if (
                st.session_state.body1 == "Custom"
                and st.session_state.body2 == "Custom"
            ):
                st.session_state.map_body_positions.append((cx, cy))
                if len(st.session_state.map_body_positions) > 2:
                    st.session_state.map_body_positions = [(cx, cy)]
                if len(st.session_state.map_body_positions) == 2:
                    p1, p2 = st.session_state.map_body_positions
                    sep = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
                    st.session_state.separation = max(0.1, float(sep))
                    st.session_state.map_placement_notice = True
                st.rerun()

    if st.session_state.trajectory is not None:
        traj = st.session_state.trajectory
        # max deviation from the FIRST point of the trajectory
        start_pt = traj[0]
        devs = np.sqrt(
            (traj[:, 0] - start_pt[0]) ** 2 + (traj[:, 1] - start_pt[1]) ** 2
        )
        max_dev = np.max(devs)

        st.html("""
        <div class="section-head">
          <div><div class="eyebrow">Mission data</div><div class="section-head__title">Telemetry readout</div></div>
          <div class="section-head__detail">3 ORBITAL PERIODS</div>
        </div>
        """)
        with st.container(border=True):
            r_col1, r_col2, r_col3, r_col4 = st.columns(4)
            r_col1.metric("Max Deviation", f"{max_dev:.6f} AU")
            r_col2.metric("Jacobi Constant", f"{jacobi_val:.6f}")
            r_col3.metric("Mass Ratio (μ)", f"{mu:.6f}")

            m_total = m1_val + m2_val
            omega = np.sqrt(1.0 * m_total / (separation**3))
            period = 2.0 * np.pi / omega
            r_col4.metric("Orbital Period", f"{period:.4f} yrs")
