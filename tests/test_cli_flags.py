import subprocess
def test_scripts_help():
    for s in ["bridge_startup_yc_evidence","compare_agent_counts","convert_250_to_viz"]:
        r = subprocess.run(["python3",f"scripts/{s}.py","-h"], capture_output=True, timeout=5)
        assert r.returncode == 0
