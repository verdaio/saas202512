# Git Automation - Commit & Push Workflow

**IMPORTANT:** This project is connected to GitHub. After creating or updating documentation, automatically commit and push changes.

---

## When to Auto-Commit & Push

**Always commit and push after:**
- ✅ Creating planning documents (roadmaps, PRDs, sprint plans, OKRs)
- ✅ Updating existing documentation (any .md files)
- ✅ Creating technical specs (ADRs, API specs, architecture docs)
- ✅ Adding meeting notes or retrospectives
- ✅ Updating project state (.project-state.json)
- ✅ Any file changes the user requested

**Do NOT auto-commit for:**
- ❌ Code implementation (ask user first: "Ready to commit this code?")
- ❌ Configuration changes (.env, secrets, credentials)
- ❌ Dependency updates (package.json, requirements.txt)
- ❌ Database migrations or schema changes

---

## Commit Message Format

Use clear, descriptive commit messages:

```bash
# Documentation
git commit -m "docs: add initial product roadmap"
git commit -m "docs: update sprint 1 plan with user stories"
git commit -m "docs: create API specification for auth endpoints"

# Planning
git commit -m "plan: add Q1 OKRs and success metrics"
git commit -m "plan: update project brief with user feedback"

# Updates
git commit -m "update: mark sprint 1 stories as completed"
git commit -m "update: add ADR for database selection"
```

---

## Standard Workflow

After creating/updating any documentation files:

```bash
# 1. Check status (optional, for awareness)
git status

# 2. Stage all changes
git add .

# 3. Commit with descriptive message
git commit -m "docs: <clear description of what was added/changed>"

# 4. Push to GitHub
git push origin master

# 5. Confirm to user
echo "✅ Changes committed and pushed to GitHub"
```

---

## Example

```bash
# After creating roadmap
cd /c/devop/saas202512
git add .
git commit -m "docs: add initial product roadmap and sprint 1 plan"
git push origin master
```

**Tell user:** "✅ Documentation saved and pushed to GitHub at https://github.com/ChrisStephens1971/saas202512"

---

## Error Handling

If push fails:
1. Check if you're on the right branch: `git branch`
2. Pull latest changes: `git pull origin master`
3. Resolve conflicts if any
4. Push again: `git push origin master`
5. If still failing, inform user and ask for help
