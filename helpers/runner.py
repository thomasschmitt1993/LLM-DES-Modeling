import subprocess, sys, tempfile, textwrap
from pathlib import Path

def run_python_code(code_str: str, timeout = 300):
    # Write the generated code to a scratch file
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".py",
                                     encoding="utf-8") as tmp:
        tmp.write(textwrap.dedent(code_str))
        tmp_path: Path = Path(tmp.name)

    # Launch a new interpreter so the code runs in isolation
    result = subprocess.run(
        [sys.executable, str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    # check if things go well and delete the file if it does.
    if result.returncode == 0:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
    if result.returncode != 0:
        raise RuntimeError(
            f"{tmp_path} exited {result.returncode}:\n{result.stderr}")
    return result.stdout