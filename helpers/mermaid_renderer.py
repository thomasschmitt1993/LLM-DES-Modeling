import subprocess
import os
import shutil

def render_mermaid_to_png(mmd_path, output_path):
    if not os.path.exists(mmd_path):
        raise FileNotFoundError(f".mmd file not found: {mmd_path}")

    if shutil.which("npx") is None:
        raise RuntimeError("npx not found. Install Node.js to use this renderer.")

    cmd = [
        "npx", "--yes",
        "@mermaid-js/mermaid-cli",
        "-i", mmd_path,
        "-o", output_path
    ]

    print(f"Rendering Mermaid diagram: {mmd_path} → {output_path}")
    subprocess.run(cmd, check=True)
    print("Rendering complete.")