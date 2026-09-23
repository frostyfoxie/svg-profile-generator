#!/usr/bin/env python3
"""Run the upstream profile generator without requiring users to install anything."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

SOURCE_REPO = "frostyfoxie/frostyfoxie"
SOURCE_FILES = ("scripts/update_svg.py", "template.svg")


def download(path: str, ref: str, destination: Path) -> None:
    url = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{ref}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "svg-profile-generator-action"})
    with urllib.request.urlopen(request, timeout=30) as response:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.read())


def main() -> int:
    username = os.environ["INPUT_USERNAME"].strip()
    token = os.environ["INPUT_GITHUB_TOKEN"].strip()
    config_path = Path(os.environ["INPUT_CONFIG_PATH"])
    output_dir = Path(os.environ["INPUT_OUTPUT_DIRECTORY"])
    source_ref = os.environ["INPUT_SOURCE_REF"].strip()

    if not username:
        raise SystemExit("username must not be empty")
    if not token:
        raise SystemExit("github-token must not be empty")
    if not source_ref:
        raise SystemExit("source-ref must not be empty")

    workspace = Path.cwd()
    output_dir = output_dir if output_dir.is_absolute() else workspace / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="svg-profile-generator-") as temp:
        root = Path(temp)
        for source_file in SOURCE_FILES:
            download(source_file, source_ref, root / source_file)

        # The upstream generator reads config.json from its own root.
        if config_path.exists():
            shutil.copy2(config_path, root / "config.json")
        else:
            (root / "config.json").write_text("{}\n", encoding="utf-8")
            print(f"No {config_path} found; using the built-in defaults.")

        env = os.environ.copy()
        env.update({"GH_USERNAME": username, "GITHUB_TOKEN": token})
        subprocess.run([sys.executable, str(root / "scripts/update_svg.py")], cwd=root, env=env, check=True)

        for filename in ("profile.svg", "btn_github.svg", "btn_instagram.svg", "btn_email.svg"):
            shutil.copy2(root / filename, output_dir / filename)
            print(f"Wrote {output_dir / filename}")


if __name__ == "__main__":
    main()
