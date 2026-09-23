# SVG Profile Generator

Create a polished, animated GitHub profile SVG that updates itself from your real GitHub data.

**Goal: minimum setup.** No Python installation, packages, API server, or manual data entry is required.

## ⚡ 2-minute setup

### 1. Add the workflow

In your GitHub profile repository:

**Actions → New workflow → create a workflow → paste this:**

```yaml
name: Update GitHub Profile SVG

on:
  schedule:
    - cron: '17 */6 * * *'
  workflow_dispatch:
  push:
    paths:
      - '.github/profile.json'

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: frostyfoxie/svg-profile-generator@v1
```

Click **Commit changes**.

### 2. Show the SVG

Add this anywhere in your profile `README.md`:

```markdown
![My animated GitHub profile](./profile.svg)
```

### 3. Done

The action generates:

- `profile.svg`
- `btn_github.svg`
- `btn_instagram.svg`
- `btn_email.svg`

It automatically refreshes on the schedule above and can also be run manually from **Actions → Update GitHub Profile SVG → Run workflow**.

> **Permissions:** the workflow needs `contents: write` so the generated SVG can be committed back to the repository.

## ✨ Customize it — optional

You can use the default design with **zero configuration**.

If you want to personalize it, create `.github/profile.json`:

```json
{
  "contact": {
    "instagram": "your_handle",
    "email": "you@example.com"
  },
  "behind_the_code": {
    "subheading": "STUDENT · CREATOR · CURIOUS MIND",
    "description": [
      "I build difficult things and care about polished interfaces."
    ]
  },
  "achievements": [
    {
      "year": "2026",
      "title": "Achievement title",
      "description": "Short supporting detail"
    }
  ],
  "skills": ["Python", "Web Development"],
  "tech_stack": ["python", "github", "html"]
}
```

### Configuration

| Field | Required | Purpose |
| --- | --- | --- |
| `contact` | No | Instagram and email shown in the buttons |
| `behind_the_code` | No | Subtitle and short profile description |
| `achievements` | No | Timeline shown under **Achievements** |
| `skills` | No | Skill pills |
| `tech_stack` | No | Technology icons |

All fields are optional. Omit them and the built-in defaults are used.

## 🔧 Advanced inputs

The normal setup does not require any inputs.

| Input | Default | Purpose |
| --- | --- | --- |
| `github-token` | `${{ github.token }}` | GitHub API access |
| `username` | `${{ github.repository_owner }}` | Account represented by the card |
| `config-path` | `.github/profile.json` | Configuration file |
| `output-directory` | `.` | SVG destination |
| `commit` | `true` | Commit generated SVGs |

For private repository data, provide a suitable token through `github-token`. Never put tokens in `profile.json`.

## 📦 Marketplace

This repository is structured as a GitHub Action with the required root `action.yml`.

For a Marketplace release:

1. Keep the repository public.
2. Create a semantic-version release such as `v1.0.0`.
3. Select **Publish this Action to the GitHub Marketplace**.
4. Choose a category and publish.
5. Keep the `v1` major tag pointing to the latest compatible release.

See GitHub's documentation for the current Marketplace publishing requirements.

## License / attribution

The generator uses the profile template and generator from [frostyfoxie/frostyfoxie](https://github.com/frostyfoxie/frostyfoxie). Please retain the applicable attribution and license terms when distributing or modifying the generator.
