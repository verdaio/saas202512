# Contributing Guide - Pet Care Scheduler

**Last Updated:** 2025-11-02
**Project:** saas202512 (Pet Care)

Thank you for contributing to Pet Care Scheduler! This guide ensures consistency and quality across the codebase.

---

## Table of Contents

- [File Naming Conventions](#file-naming-conventions)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## File Naming Conventions

We use **consistent naming conventions** based on folder purpose. Follow these rules:

### General Rule

| Folder | Convention | Examples |
|--------|------------|----------|
| **docs/** | Title Case | `Developer-Guide.md`, `Testing-Guide.md` |
| **quick-reference/** | UPPER-KEBAB | `DOCKER-COMMANDS.md`, `GIT-WORKFLOW.md` |
| **scripts/** | lower-kebab | `seed-data.sh`, `backup-db.ps1` |
| **sprints/** | lower-kebab | `sprint-01-foundation.md` |
| **product/** | lower-kebab | `roadmap-template.md`, `prd-template.md` |
| **business/** | lower-kebab | `okr-template.md` |
| **technical/** | lower-kebab | `adr-template.md`, `api-spec-template.md` |

### Specific Examples

**✅ Good:**
```
docs/Developer-Guide.md
docs/Contributing.md
docs/Security.md
quick-reference/DOCKER-COMMANDS.md
quick-reference/API-ENDPOINTS.md
scripts/seed-dev-data.sh
scripts/backup-database.ps1
sprints/current/sprint-01-foundation.md
product/roadmap/2025-Q1-roadmap.md
```

**❌ Bad:**
```
docs/developer_guide.md          # Use Title-Case
docs/DEVELOPER-GUIDE.md          # Use Title-Case (not UPPER)
quick-reference/docker-commands.md  # Use UPPER-KEBAB
scripts/SeedData.sh              # Use lower-kebab
sprints/current/Sprint-01.md     # Use lower-kebab
```

### Source Code Files

**Backend (Python):**
- Modules: `snake_case` (e.g., `user_service.py`)
- Classes: `PascalCase` (e.g., `class UserService`)
- Functions: `snake_case` (e.g., `def get_user()`)

**Frontend (TypeScript/React):**
- Components: `PascalCase` (e.g., `BookingWidget.tsx`)
- Utilities: `camelCase` (e.g., `formatDate.ts`)
- Hooks: `camelCase` with `use` prefix (e.g., `useAuth.ts`)

---

## Code Style

### Indentation Standards

**Use 2 spaces** for Markdown and YAML. Use 4 spaces for Python. Use 2 spaces for JavaScript/TypeScript.

**Markdown (2 spaces):**
```markdown
## Heading

- Item 1
  - Sub-item 1.1
    - Sub-sub-item 1.1.1
  - Sub-item 1.2
- Item 2
```

**YAML (2 spaces):**
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5412:5432"
```

**Python (4 spaces):**
```python
def calculate_total(items):
    total = 0
    for item in items:
        if item.is_active:
            total += item.price
    return total
```

**TypeScript/JavaScript (2 spaces):**
```typescript
function BookingWidget() {
  const [date, setDate] = useState(null);

  return (
    <div>
      <DatePicker onChange={setDate} />
    </div>
  );
}
```

### Formatting Tools

- **Python:** Use `black` and `isort`
- **TypeScript:** Use `prettier` and `eslint`
- **Markdown:** Use `prettier` (2 spaces)

---

## Commit Messages

We follow **Conventional Commits** for clear, semantic commit history.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Use When | Example |
|------|----------|---------|
| `feat` | New feature | `feat(booking): add multi-pet selection` |
| `fix` | Bug fix | `fix(auth): resolve token expiration issue` |
| `docs` | Documentation only | `docs: update developer guide` |
| `style` | Code style (formatting, no logic change) | `style: fix indentation in user service` |
| `refactor` | Code refactoring (no new features or fixes) | `refactor(scheduling): extract availability logic` |
| `perf` | Performance improvement | `perf(api): add database query caching` |
| `test` | Add or update tests | `test(booking): add integration tests` |
| `build` | Build system or dependencies | `build: upgrade fastapi to 0.110.0` |
| `ci` | CI/CD changes | `ci: add docker build step to github actions` |
| `chore` | Maintenance tasks | `chore: update .gitignore` |

### Scope (Optional)

Use scope to indicate what part of the codebase is affected:
- `booking`, `auth`, `scheduling`, `payment`, `sms`, `vaccination`
- `api`, `ui`, `db`, `infra`

### Examples

**Good commits:**
```bash
feat(booking): add two-tap reschedule via SMS
fix(scheduling): prevent double-booking race condition
docs: add security guidelines for secrets management
test(payment): add Stripe webhook integration tests
refactor(api): extract tenant resolution to middleware
```

**Bad commits:**
```bash
update code           # Too vague
fix bug              # What bug? Where?
WIP                  # Work in progress, don't commit yet
asdfasdf             # Meaningless
```

### Commit Footer

Include references to issues or breaking changes:

```bash
feat(auth): add OAuth2 support

Add OAuth2 authentication flow using Stripe Connect.

Closes #42
```

```bash
refactor(api)!: change appointment response format

BREAKING CHANGE: Appointment API now returns ISO 8601 timestamps
instead of Unix epoch. Update all clients.
```

---

## Pull Requests

### PR Size Guidelines

**Keep PRs small and focused.** Aim for:
- ✅ **Small:** <200 lines changed (ideal)
- ⚠️ **Medium:** 200-500 lines changed (acceptable)
- ❌ **Large:** >500 lines changed (split if possible)

**Exceptions:** Generated files, migrations, dependencies

### PR Title

Follow Conventional Commits format:

```
feat(booking): add multi-pet appointment support
```

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Added multi-pet selection to booking widget
- Updated appointment model to support multiple pets
- Added validation for pet capacity

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Tested manually in local environment

## Screenshots (for UI changes)
[Attach screenshots for any visual changes]

## Generated Artifacts (if applicable)
- [ ] Screenshot of generated .docx file included
- [ ] Verified output matches expected format

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated (if needed)
- [ ] No secrets in code or config
- [ ] Database migrations included (if schema changed)
- [ ] `docker compose config` validates without errors (if infra changed)
```

### PR Labels

Use these labels to categorize PRs:

| Label | Use When |
|-------|----------|
| `enhancement` | New feature or improvement |
| `bug` | Bug fix |
| `documentation` | Documentation changes only |
| `infrastructure` | Docker, CI/CD, deployment |
| `security` | Security-related changes |
| `dependencies` | Dependency updates |
| `breaking-change` | Breaking API or schema changes |
| `needs-review` | Ready for review |
| `work-in-progress` | Not ready for review yet |

### Screenshots Requirement

**Required for:**
- UI changes (new components, styling updates)
- Generated documents (.docx, .pdf, reports)
- Email/SMS templates
- Dashboard or visualization changes

**Format:**
- Use markdown image syntax: `![Description](url)`
- Or attach directly to PR
- Show before/after for changes

**Example:**
```markdown
## Screenshots

### Before
![Old booking widget](screenshots/before.png)

### After
![New multi-pet booking widget](screenshots/after.png)
```

### Review Process

1. **Self-review:** Review your own PR first
2. **Automated checks:** Ensure CI passes (tests, linting)
3. **Peer review:** Request review from teammate (if applicable)
4. **Address feedback:** Make requested changes
5. **Merge:** Squash and merge (or merge commit for feature branches)

---

## Testing Requirements

All PRs must include tests. See `docs/Testing-Guide.md` for details.

### Minimum Requirements

**Backend PRs:**
- Unit tests for new functions/classes
- Integration tests for API endpoints
- Coverage should not decrease

**Frontend PRs:**
- Component tests for new UI
- Integration tests for user flows
- Snapshot tests for complex components

**Infrastructure PRs:**
- Validate `docker compose config`
- Test deployment in staging environment
- Document any manual steps

### Smoke Tests

Run these before submitting PR:

```bash
# Backend
pytest
curl http://localhost:8012/health

# Frontend
npm test
curl http://localhost:3012

# Docker
docker compose config
docker compose up -d
docker compose ps  # All services should be "running"
```

---

## Documentation

### When to Update Docs

Update documentation when you:
- Add new features (update relevant PRD or sprint plan)
- Change architecture (create ADR in `technical/adr/`)
- Update infrastructure (update `docs/Developer-Guide.md`)
- Change API contracts (update API specs)
- Add new dependencies (update Developer Guide prerequisites)

### Architecture Decision Records (ADRs)

**Required for:**
- Database schema changes
- Technology choices (libraries, frameworks)
- Infrastructure changes (hosting, deployment)
- Security decisions (auth method, encryption)
- API design changes

**Template:** `technical/adr-template.md`

**Naming:** `technical/adr/YYYY-MM-DD-decision-title.md`

**Example:** `technical/adr/2025-01-15-use-twilio-for-sms.md`

### Documentation Standards

- **Use Term "Artifacts" Consistently**
  - ✅ "Generated artifacts" (not "generated files" or "output")
  - ✅ "Build artifacts" (not "build outputs")

- **Keep Documentation Up-to-Date**
  - Update docs in the same PR as code changes
  - Don't create stale documentation

- **Link to Related Docs**
  - Reference `technical/multi-tenant-architecture.md` for tenant-related decisions
  - Reference sprint plans for feature context
  - Cross-link related documentation

---

## Generated Files Policy

### Files to Commit

**✅ Commit these:**
- Documentation (.md files)
- Configuration templates (.example files)
- Database migrations (Alembic)
- Build manifests (package.json, requirements.txt)

### Files NOT to Commit

**❌ Do NOT commit these:**
- Environment files (.env - use .env.example instead)
- Build outputs (dist/, build/, __pycache__/)
- Node modules (node_modules/)
- Python virtual environments (venv/, .venv/)
- Generated artifacts (unless explicitly required for review)

### Generated Documents (.docx, .pdf)

**Policy:** Do NOT commit generated documents to main branch.

**For PRs requiring review of generated output:**
1. Generate the file locally
2. Take screenshot showing the output
3. Include screenshot in PR description
4. Do NOT commit the .docx/.pdf file itself

**Reason:** Generated binary files bloat repository and create merge conflicts.

**Exception:** If project specifically requires committing generated docs, add to .gitignore exceptions.

---

## Code Review Guidelines

### As a Reviewer

- **Be constructive:** Suggest improvements, don't just criticize
- **Explain why:** Help the author learn
- **Use labels:** Mark comments as "nit" (minor), "question", "blocker"
- **Approve quickly:** Don't let PRs stagnate

### As an Author

- **Respond to all comments:** Even if just to acknowledge
- **Don't take it personally:** Reviews improve code quality
- **Ask questions:** If feedback is unclear, ask for clarification
- **Update PR:** Address all feedback before re-requesting review

---

## Questions?

- Check `docs/Developer-Guide.md` for setup and troubleshooting
- Check `docs/Testing-Guide.md` for testing requirements
- Check `docs/Security.md` for security best practices
- Create GitHub issue if you need help

---

**Thank you for contributing!** 🎉
