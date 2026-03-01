# spec-audit-loop-skill

Reusable Codex skill: `spec-audit-loop`.

This skill runs a spec-first implementation workflow with independent Spark audits, gray-box checks, evidence gates, and progress rejudge to reduce false `DONE` status.

## Contents

- `spec-audit-loop/SKILL.md`
- `spec-audit-loop/agents/openai.yaml`
- `spec-audit-loop/references/templates.md`
- `spec-audit-loop/scripts/progress_rejudge.py`

## Install (Codex Skill Installer)

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo hyophyop/spec-audit-loop-skill \
  --path spec-audit-loop
```

After install, restart Codex.

## Version

Current contract in skill docs: `spec-audit-loop@2026.03.01`

## License

MIT
