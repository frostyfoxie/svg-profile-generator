#!/usr/bin/env python3
"""Run the upstream profile generator with zero-install setup and resilient icon handling."""
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

DEFAULT_CONFIG = {
    "_setup": "Generated automatically by SVG Profile Generator. Replace the mock profile fields with your own data.",
    "contact": {"instagram": "your_instagram", "email": "you@example.com"},
    "behind_the_code": {
        "subheading": "STUDENT · CREATOR · AI ENTHUSIAST",
        "description": [
            "I build ambitious software projects, explore AI, and care about polished user experiences."
        ],
    },
    "achievements": [
        {
            "year": "2026",
            "title": "Project milestone",
            "description": "Replace this with a real achievement, competition, certification, or milestone.",
        },
        {
            "year": "2025",
            "title": "Learning milestone",
            "description": "Replace this with another real achievement or experience.",
        },
    ],
    "skills": ["Python", "JavaScript", "AI / ML", "UI / UX", "Git", "Problem Solving"],
    "tech_stack": [
        "python", "javascript", "typescript", "react", "nextdotjs",
        "github", "git", "html5", "css3"
    ],
}

FALLBACK_EMAIL_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#475569" d="M2.5 5.5A2.5 2.5 0 0 1 5 3h14a2.5 2.5 0 0 1 2.5 2.5v13A2.5 2.5 0 0 1 19 21H5a2.5 2.5 0 0 1-2.5-2.5v-13Zm2.8-.2 6.7 5.15 6.7-5.15H5.3Zm13.7 13.2V8.25l-6.08 4.68a1.5 1.5 0 0 1-1.84 0L5 8.25v10.25c0 .39.31.7.7.7h12.6c.39 0 .7-.31.7-.7Z"/></svg>"""


def download(path: str, ref: str, destination: Path) -> None:
    url = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{ref}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "svg-profile-generator-action"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(response.read())
    except Exception as exc:
        raise RuntimeError(
            f"Could not download the pinned generator asset '{path}'. "
            f"Check network access and source-ref '{ref}'."
        ) from exc


def ensure_config(config_path: Path, destination: Path) -> None:
    """Create the public config on first run, then translate it for the renderer."""
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Created {config_path} with editable mock profile data.")
        print("Replace the mock contact, bio, achievements, skills and tech stack, then run the workflow again.")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {config_path}: {exc}") from exc

    if "achievements" in config and "education" not in config:
        translated = []
        for item in config.get("achievements", []):
            item = dict(item)
            if "institution" not in item and "description" in item:
                item["institution"] = item["description"]
            translated.append(item)
        config["education"] = translated

    destination.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def download_simpleicon(slug: str, destination: Path) -> bool:
    url = f"https://cdn.simpleicons.org/{slug}"
    request = urllib.request.Request(url, headers={"User-Agent": "svg-profile-generator-action"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            data = response.read()
            if not data:
                return False
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            print(f"Fetched icon '{slug}' from the internet.")
            return True
    except Exception as exc:
        print(f"Warning: could not fetch internet icon '{slug}': {exc}")
        return False


def prepare_icons(source_icons_dir: Path, destination_icons_dir: Path, config_path: Path) -> None:
    """Prefer user-uploaded icons, otherwise fetch missing icons from Simple Icons."""
    destination_icons_dir.mkdir(parents=True, exist_ok=True)

    if source_icons_dir.exists():
        for item in source_icons_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, destination_icons_dir / item.name)
                print(f"Loaded custom icon from icons/{item.name}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    requested = {str(x).strip().lower() for x in config.get("tech_stack", []) if str(x).strip()}
    requested.update({"github", "instagram"})

    for slug in sorted(requested):
        if any(
            (destination_icons_dir / f"{slug}{ext}").exists()
            for ext in (".svg", ".png", ".webp", ".jpg", ".jpeg")
        ):
            continue
        download_simpleicon(slug, destination_icons_dir / f"{slug}.svg")

    email_candidates = [
        destination_icons_dir / f"email{ext}"
        for ext in (".svg", ".png", ".webp", ".jpg", ".jpeg")
    ]
    if not any(p.exists() for p in email_candidates):
        (destination_icons_dir / "email.svg").write_text(FALLBACK_EMAIL_SVG, encoding="utf-8")
        print("Using built-in email icon. Add icons/email.svg to override it.")


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
    config_path = config_path if config_path.is_absolute() else workspace / config_path
    output_dir = output_dir if output_dir.is_absolute() else workspace / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="svg-profile-generator-") as temp:
        root = Path(temp)

        for source_file in SOURCE_FILES:
            download(source_file, source_ref, root / source_file)

        ensure_config(config_path, root / "config.json")
        prepare_icons(workspace / "icons", root / "icons", config_path)

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
