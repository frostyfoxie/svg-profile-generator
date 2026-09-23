# SVG Profile Generator

Create a polished, animated GitHub profile card and keep it updated automatically. The action downloads no packages, requires no Python setup, and can commit the generated SVGs for you.

## Quick start

1. In your profile repository, open **Actions → New workflow → SVG Profile Generator**.
2. Click **Commit changes**.
3. Open `README.md` and add:

```markdown
![My animated GitHub profile](./profile.svg)
```

That is all. The workflow runs on pushes, on a schedule, and manually from the Actions tab.

You can also add this minimal workflow yourself:

```yaml
name: Update SVG profile

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

## Customize it

Create `.github/profile.json` to customize the card. Any omitted value uses a default:

```json
{
  "contact": {
    "instagram": "your_handle",
    "email": "you@example.com"
  },
  "behind_the_code": {
    "subheading": "DEVELOPER · CREATOR · CURIOUS MIND",
    "description": ["I build useful things.", "I enjoy learning in public."]
  },
  "education": [],
  "skills": ["Python", "Web Development"],
  "tech_stack": ["python", "github", "html"]
}
```

The action creates `profile.svg`, `btn_github.svg`, `btn_instagram.svg`, and `btn_email.svg` in the repository root. To place them elsewhere, set `output-directory`.

### Inputs

| Input | Default | Purpose |
| --- | --- | --- |
| `github-token` | `${{ github.token }}` | Reads GitHub profile and contribution data |
| `username` | `${{ github.repository_owner }}` | Account represented by the card |
| `config-path` | `.github/profile.json` | Optional JSON configuration |
| `output-directory` | `.` | Destination for generated SVGs |
| `commit` | `true` | Automatically commit and push changed SVGs |

For private repository data, provide a suitable token through `github-token`. Never put tokens in `profile.json`.

## Marketplace release checklist

This repository contains the root `action.yml` and a workflow template. To publish it, create a semver release such as `v1.0.0`, select **Publish this Action to the GitHub Marketplace**, choose a category, and publish. Keep the moving major tag `v1` pointing at the latest compatible release.

The generator is based on [frostyfoxie/frostyfoxie](https://github.com/frostyfoxie/frostyfoxie), whose attribution license applies to the generated template and assets.
