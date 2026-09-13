import PyInstaller.__main__
import sys
import os
import shutil

if __name__ == "__main__":
    # Ensure build is clean
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    os_name = "windows" if sys.platform == "win32" else "mac"
    exe_name = f"Celestia-{os_name}"

    args = [
        "run_app.py",
        "--name", exe_name,
        "--onefile",
        "--windowed", # Don't open a console window if possible
        "--copy-metadata", "streamlit",
        "--copy-metadata", "plotly",
        "--collect-all", "streamlit",
        "--collect-all", "plotly",
        "--collect-all", "manim",
        "--collect-all", "rebound",
        "--collect-all", "scipy",
        "--collect-all", "numpy",
        "--hidden-import", "manim_viz",
        "--hidden-import", "physics",
        "--hidden-import", "rebound_sim",
        "--hidden-import", "viz",
        "--hidden-import", "frames",
        "--add-data", f"app.py{os.pathsep}.",
        "--add-data", f"manim_viz.py{os.pathsep}.",
        "--add-data", f"physics.py{os.pathsep}.",
        "--add-data", f"rebound_sim.py{os.pathsep}.",
        "--add-data", f"viz.py{os.pathsep}.",
        "--add-data", f"frames.py{os.pathsep}.",
        "--add-data", f"logo.png{os.pathsep}.",
    ]
    
    if os.path.exists(".streamlit"):
        args.extend(["--add-data", f".streamlit{os.pathsep}.streamlit"])

    PyInstaller.__main__.run(args)
