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


def prepare_config(config_path: Path, destination: Path) -> None:
    """Support the public 'achievements' schema while keeping the generator compatible."""
    if not config_path.exists():
        destination.write_text("{}\n", encoding="utf-8")
        print(f"No {config_path} found; using the built-in defaults.")
        return

    config = json.loads(config_path.read_text(encoding="utf-8"))

    # New public schema: achievements.
    # The current renderer still calls this internal field education, so translate
    # it here rather than exposing that implementation detail to users.
    if "achievements" in config and "education" not in config:
        translated = []
        for item in config.get("achievements", []):
            item = dict(item)
            if "institution" not in item and "description" in item:
                item["institution"] = item.pop("description")
            translated.append(item)
        config["education"] = translated

    destination.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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

        prepare_config(config_path, root / "config.json")

        # The upstream template currently uses "Education" as its visible heading.
        # Keep the public action terminology as "Achievements" without requiring
        # users to modify the upstream template.
        template_path = root / "template.svg"
        template = template_path.read_text(encoding="utf-8")
        template = template.replace(">Education</text>", ">Achievements</text>")
        template_path.write_text(template, encoding="utf-8")

        env = os.environ.copy()
        env.update({"GH_USERNAME": username, "GITHUB_TOKEN": token})

        subprocess.run(
            [sys.executable, str(root / "scripts/update_svg.py")],
            cwd=root,
            env=env,
            check=True,
        )

        for filename in (
            "profile.svg",
            "btn_github.svg",
            "btn_instagram.svg",
            "btn_email.svg",
        ):
            shutil.copy2(root / filename, output_dir / filename)
            print(f"Wrote {output_dir / filename}")


if __name__ == "__main__":
    main()
