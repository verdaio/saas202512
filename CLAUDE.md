# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

---

## 🎯 Role Division

**You (the user) make decisions:**
- What features to build
- What the product does
- Business priorities
- Any choices or direction

**Claude (the AI) does all computer work:**
- Planning documents (roadmaps, PRDs, sprint plans)
- Coding and implementation
- Documentation
- Technical sequencing (what to build in what order)
- File creation and organization

**Simple rule:** When there's a decision to make, Claude asks. Everything else, Claude just does.

---

## 📏 Documentation Standards

### ⚠️ CRITICAL: File Length Guideline

**Target: Keep all documentation files under 650 lines**

**Why this matters:**
- Easier to read and navigate
- Faster to load and process
- Better for maintainability
- Forces clarity and conciseness

**Exceptions (comprehensive guides allowed to exceed):**
- ✅ `DEVELOPMENT-GUIDE.md` (complete tooling and setup)
- ✅ `STYLE-GUIDE.md` (exhaustive style reference)
- ✅ `MCP-SETUP-GUIDE.md` (complete MCP documentation)
- ✅ Tutorial/training documents

**For all other documentation:**
- ❌ PRDs, sprint plans, ADRs, meeting notes
- ❌ API specs, tech specs, test plans
- ❌ Product roadmaps, OKRs, user research

**If a doc exceeds 650 lines:**
1. Split into multiple focused documents
2. Create a parent doc with links to child docs
3. Move detailed sections to separate files
4. Keep main doc as overview/index

**Example:**
```
# Bad: Single 900-line API spec
api-spec.md (900 lines)

# Good: Split into focused docs
api-spec.md (150 lines - overview)
api-spec-authentication.md (200 lines)
api-spec-user-endpoints.md (180 lines)
api-spec-payment-endpoints.md (220 lines)
```

---

## 📖 Essential Project Guides

**Before starting any work, familiarize yourself with these guides:**

| Guide | Purpose | Reference When |
|-------|---------|----------------|
| **DEVELOPMENT-GUIDE.md** | Tooling requirements, Docker setup, diagnostics | Setting up environment, troubleshooting infrastructure |
| **STYLE-GUIDE.md** | File naming, code style, formatting standards | Creating files, writing code, naming conventions |
| **TESTING-CHECKLIST.md** | Pre-commit checks, smoke tests, validation | Before commits, before deployment |
| **.gitignore** | What gets committed vs ignored | Understanding generated files policy |

**Key Standards:**
- **Tooling:** Node.js 18+, npm 9+, Docker Compose v2+, Azure CLI 2.60+ (see DEVELOPMENT-GUIDE.md)
- **File Naming:** Varies by directory - UPPER-KEBAB for quick-reference/, kebab-case for templates (see STYLE-GUIDE.md)
- **Generated Files:** Commit `.docx` in fundraising/, ignore `.pdf` exports (see .gitignore comments)
- **Code Style:** Follow `C:\devop\coding_standards.md` - 2-space indentation for JS/YAML/JSON, camelCase for JS, snake_case for Python
- **Testing:** Run `npm run lint && npm test && npm run build` before commits (see TESTING-CHECKLIST.md)

**Quick Diagnostics:**
```bash
# Validate Docker Compose changes
docker compose config

# Check service health
docker compose ps
docker compose logs -f [service]

# Pre-commit validation
npm run lint && npm test && npm run build
```

---

## 🏢 Multi-Tenant Architecture

**Multi-Tenant Enabled:** true
**Tenant Model:** subdomain

### Important Considerations

**When working on this project, always remember:**

- **Database schemas:** All tables (except system tables) must include `tenant_id` column
- **API endpoints:** All endpoints must be tenant-scoped (filter by tenant)
- **Authentication:** Tokens and sessions must include tenant context
- **File storage:** Files must be stored with tenant prefix (e.g., `s3://bucket/{tenant-id}/...`)
- **Testing:** Always test cross-tenant isolation

**See detailed documentation:** `technical/multi-tenant-architecture.md`

---

## 🎯 Project Setup

**Project ID:** saas202512
**Created:** 2025-11-02
**Status:** active

For detailed project setup workflows including first-time detection, quick start mode, and detailed setup mode, see:

**→ `.config/PROJECT-SETUP-GUIDE.md`**

**Quick summary:**
- First-time users get greeted and offered Quick Start (5 min) or Detailed Setup (15-20 min)
- Detailed setup includes discovery questions, roadmap creation, sprint planning, and OKRs
- Adapts to solo/team and MVP-first/complete-build/growth-stage approaches

---

## 🎯 Integration Resources

**This project integrates multiple layers of capabilities:**

| Layer | What | Details |
|-------|------|---------|
| **Tier 1** | Virtual Agents (below) | Always loaded, planning & documentation |
| **Tier 2** | Claude Code Templates | 163 agents, 210 commands - On-demand technical specialists |
| **Tier 3** | Claude Skills | Optional document processing & specialized tasks |

**Quick setup:**
```bash
# Install Claude Code Templates (on-demand)
npx claude-code-templates@latest --agent development-team/frontend-developer
npx claude-code-templates@latest --command testing/generate-tests

# Install Claude Skills (optional)
/plugin marketplace add anthropics/skills
```

**For detailed integration guides:**
- **Claude Code Templates:** `.config/claude-code-templates-guide.md` ← **Recommended for development**
- Claude Skills: `.config/recommended-claude-skills.md`
- All integrations: `.config/INTEGRATIONS.md`

### 🎯 When to Use What

| Your Need | Use This | Example |
|-----------|----------|---------|
| **Planning & Documentation** | Built-in Virtual Agents | "Plan sprint 1", "Write PRD for auth" |
| **Technical Implementation** | Claude Code Templates | Install frontend-developer, backend-architect |
| **Testing & QA** | Claude Code Templates | `/generate-tests`, `/e2e-setup` |
| **Security Audits** | Claude Code Templates | Install security-auditor agent |
| **Specialized Tasks** | Claude Skills | Document processing (PDF, Excel, etc.) |
| **Advanced Specialists** | See `docs/advanced/` | Framework-specific, payments, AI features |

---


---

## 🔒 Azure Security Baseline

This project includes the **Azure Security Playbook v2.0** - a comprehensive zero-to-production security implementation.

### Security Resources

**📘 Core Documentation:**
- `technical/azure-security-zero-to-prod-v2.md` - Complete security playbook (Days 0-9)
- `azure-security-baseline-checklist.csv` - 151-task tracking checklist

**🚨 Incident Response Runbooks:**
- `azure-security-runbooks/` - 5 detailed incident response procedures
  - credential-leak-response.md (MTTR: 15 min)
  - exposed-storage-response.md (MTTR: 30 min)
  - suspicious-consent-response.md (MTTR: 20 min)
  - ransomware-response.md (MTTR: Immediate)
  - privilege-escalation-response.md (MTTR: 30 min)

**🏗️ Security Baseline IaC:**
- `infrastructure/azure-security-bicep/` - Production-ready Bicep modules (Recommended)
  - Deploy: `az deployment sub create --template-file azure-security-bicep/main.bicep`
- `infrastructure/azure-security-terraform/` - Terraform reference modules

**Cost:** ~$5,000-6,000/month (production) | ~$1,000-1,500/month (dev/test)

## 🤖 Virtual Agents

For detailed virtual agent workflows, triggers, and delegation patterns, see:

**→ `.config/VIRTUAL-AGENTS-GUIDE.md`**

**Available agents:**
- Sprint Planner 🏃 - Plan sprints and user stories
- PRD Assistant 📝 - Create product requirements
- Template Finder 🔍 - Find the right template
- Multi-Doc Generator 📚 - Generate complete doc sets
- System Architect 🏗️ - Document technical decisions
- Research Assistant 🔬 - Research and compare options
- QA Testing Agent 🧪 - Create test plans
- Project Manager 📊 - Track progress and status
- Documentation Agent 📖 - Write technical docs

**Key principle:** Virtual agents handle planning and documentation. For technical implementation, use Claude Code Templates (163 agents, 210 commands).

---

## 📝 Key Conventions

**File Naming:**
- Dates: `YYYY-MM-DD` format
- Templates: `*-template.md` suffix
- Examples: `example-*.md` prefix
- Drafts: `/drafts/` subfolder

**Writing Style:**
- Direct, actionable, honest
- Technical founders audience
- Realistic timelines, no hype

---


---

## 💻 Coding Standards

**When writing or reviewing code, always follow our coding standards.**

**Reference:** `C:\devop\coding_standards.md`

### Quick Summary

Our standards are based on Google's Style Guides and prioritize:
- **Consistency** - Code should look like it was written by one person
- **Readability** - Code is read more than it's written
- **Maintainability** - Easy to understand months/years later

### Language-Specific Guidelines

| Language | Naming Convention | Line Length | Key Points |
|----------|------------------|-------------|------------|
| **Python** | `snake_case` (functions/vars), `PascalCase` (classes) | 80 chars | Use docstrings, type hints, specific exceptions |
| **JavaScript** | `camelCase` (functions/vars), `PascalCase` (classes) | 80-100 chars | Use `const`/`let`, JSDoc, arrow functions |
| **Java** | `camelCase` (methods), `PascalCase` (classes) | 100 chars | Use `@Override`, prefer interfaces |
| **HTML/CSS** | lowercase tags, `kebab-case` classes | - | Meaningful names, avoid IDs |

### Universal Rules

1. **Comments** - Explain WHY, not WHAT
2. **Functions** - Single responsibility, <50 lines, ≤3 parameters
3. **Error Handling** - Specific exceptions, meaningful messages, fail fast
4. **Testing** - Write tests for all features, follow AAA pattern
5. **Version Control** - Clear commit messages: `[type] description`

### When Implementing Code

**Always:**
- Read `C:\devop\coding_standards.md` before starting major development
- Use appropriate linters (pylint, eslint, checkstyle)
- Follow naming conventions for the language
- Write meaningful comments explaining complex logic
- Include tests with new code

**In Code Reviews:**
- Check naming convention adherence
- Verify proper documentation/comments
- Ensure code clarity and readability
- Confirm test coverage
- Be constructive, explain WHY when suggesting changes

**Full guide:** `C:\devop\coding_standards.md` (comprehensive examples and best practices)

---

## 🔌 MCP Integration (Optional)

**MCPs are optional helpers for development.** They let Claude access external services like GitHub, Stripe, and databases while helping you build.

**Important:** MCP tokens are for development only (helping YOU build), not for your production application.

### Quick Setup (5 Minutes)

**Recommended approach:** Shared tokens (all projects use same tokens)

1. Get a GitHub token: https://github.com/settings/tokens
2. Open Claude Desktop config: `%APPDATA%\Claude\claude_desktop_config.json`
3. Copy contents from `.mcp-config-template.json` in this project
4. Replace `<your-github-token>` with actual token
5. Restart Claude Desktop
6. Test: Ask Claude "List my GitHub repositories"

**Recommended MCPs:**
- ⭐ **GitHub** - Manage repos, issues, PRs (start here)
- **Filesystem** - Claude can read/write project files
- **PostgreSQL** - Database queries
- **Stripe** - Payment data access

**Complete guide:** See `MCP-SETUP-GUIDE.md` for detailed instructions, security best practices, and advanced per-project token isolation.

---

## 📝 Documentation Requirements

**IMPORTANT: Document all significant work.**

### When to Document

**Required documentation:**
- ✅ **After every session** with multiple tasks (use Session Progress template)
- ✅ **After completing a sprint** (use Sprint Summary template)
- ✅ **After significant tasks** (>1 hour work, use Task Completion template)
- ✅ **After major refactoring** or architectural changes
- ✅ **After resolving complex bugs**
- ✅ **After integrating new tools or libraries**

**Documentation location:**
- Session/Sprint docs: `docs/progress/`
- Task docs: `docs/tasks/`
- Architecture docs: `docs/architecture/`

### How to Document

**Option 1: Use helper script (recommended)**
```bash
cd C:\devop\.template-system\scripts
python create_documentation.py --type session
python create_documentation.py --type sprint
python create_documentation.py --type task
```

**Option 2: Manual (use templates)**
- Templates: `.template-system/templates/documentation/`
- Copy template to project docs folder
- Fill out all sections
- Save with date: `SESSION-YYYY-MM-DD.md`

**What to include:**
- Clear objectives/goals
- All files changed (created/updated/deleted)
- Results and validation
- Problems encountered and solutions
- Next steps and blockers

**Guidelines:** See `DOCUMENTATION-GUIDELINES.md` in template system for comprehensive best practices

---

## 🎯 When Helping Users

**Always:**
- Use Task tool (subagent_type=Explore) before assuming file locations
- Read templates before filling them out
- Ask clarifying questions about scope and goals
- Cross-link related documents
- Respect profile (solo vs team vs enterprise)

**Approach-based behavior:**
- **MVP-First:** Encourage speed, discourage over-planning, focus on validation
- **Complete Build:** Allow comprehensive planning, ensure all features documented upfront, emphasize quality and completeness
- **Growth-Stage:** Balance planning with execution, focus on scaling and optimization

**Never:**
- Create files without asking which template to use
- Generate generic platitudes
- Recommend over-engineering for MVPs
- Skip user research and validation

---

## 📊 Error Monitoring

For comprehensive error monitoring guidance including when to suggest Sentry vs Application Insights, see:

**→ `.config/error-monitoring-guide.md`**

**Quick summary:**
- Sentry: Best for solo/MVP with session replay
- Application Insights: Best for Azure-heavy projects
- Both: Recommended for production apps with revenue
- Trigger phrases: deploy, production, launch, going live
- Multi-tenant: Always set tenant context in errors

---

## 📧 Task Notification System

**For long-running tasks (>15 minutes), notify user via email when complete.**

**Location:** `C:\devop\scripts\` (PowerShell scripts)
**Threshold:** 15 minutes
**Email:** chris.stephens@verdaio.com

**When to use:**
- Full codebase analysis or refactoring
- Large file operations (copying, moving, searching many files)
- Complex multi-step workflows
- Any task you estimate will take >15 minutes

**Usage pattern:**

**Before starting long task:**
```powershell
cd C:\devop\scripts
.\Start-MonitoredTask.ps1 -TaskName "ClaudeCodeWork" -ThresholdMinutes 15
```

**After completing task:**
```powershell
.\Complete-MonitoredTask.ps1 -TaskName "ClaudeCodeWork"
# Sends email if task took >15 minutes
```

**Tell user:**
```
"I'll start the notification system since this might take a while. You'll receive an email at chris.stephens@verdaio.com if it takes longer than 15 minutes."
```

**Documentation:** `C:\devop\TASK-NOTIFICATION-SYSTEM.md`

---

## ⚠️ CRITICAL: Safe Process Management

**NEVER use commands that kill ALL processes of a type.**

### ❌ DANGEROUS - Never Use These

```bash
# DON'T: Kills ALL Node.js processes (including other projects)
taskkill /F /IM node.exe

# DON'T: Kills ALL matching processes
pkill -f node
pkill -f analytics
```

### ✅ SAFE - Always Use These

```powershell
# Windows - Kill by specific port
netstat -ano | findstr :3012
taskkill /F /PID <specific-PID>

# Mac/Linux - Kill by specific port
kill $(lsof -ti:3012)

# Docker - Stop only this project's containers
docker-compose down  # NOT: docker stop $(docker ps -aq)
```

**Golden Rule:** Always target processes by:
- ✅ Specific PID (from netstat/lsof)
- ✅ Specific port number (this project's ports only)
- ✅ Specific container name (`saas202512-postgres`)

**Never target by:**
- ❌ Process name (`/IM node.exe`)
- ❌ Pattern matching (`pkill -f`)
- ❌ Wildcards that affect all instances

**See full guide:** `.config/SAFE-PROCESS-MANAGEMENT.md`

**Why this matters:** Other projects, terminals, and background processes are running. Killing all Node processes affects OTHER projects and can cause data loss.

---

## 📚 Quick Reference

**Start a new project:**
1. Greet user (if first time)
2. Ask: solo/team? MVP/growth/scale?
3. Recommend: Sprint plan + PRD + OKRs
4. Guide through templates

**Plan a feature:**
1. PRD first (PRD Assistant)
2. Then: Tech Spec → API Spec → Test Plan
3. Break into user stories
4. Link to sprint

**Document a decision:**
1. Use ADR template (System Architect)
2. State: Context, Decision, Alternatives, Consequences
3. Save in `technical/adr/`

**Research and compare:**
1. Search existing docs (Research Assistant)
2. WebSearch for external info
3. Document in `product/research/` or `technical/research/`
4. Provide recommendation with trade-offs

**For implementation:** Use Claude Code Templates (see `.config/claude-code-templates-guide.md`)

**For specialized tasks:** Use Claude Skills or see `docs/advanced/SPECIALIZED-TOOLS.md`

---

## 📦 Git Automation - Commit & Push Workflow

**IMPORTANT:** This project is connected to GitHub. After creating or updating documentation, automatically commit and push changes.

### When to Auto-Commit & Push

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

### Commit Message Format

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

### Standard Workflow

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

### Example

```bash
# After creating roadmap
cd /c/devop/saas202512
git add .
git commit -m "docs: add initial product roadmap and sprint 1 plan"
git push origin master
```

**Tell user:** "✅ Documentation saved and pushed to GitHub at https://github.com/ChrisStephens1971/saas202512"

### Error Handling

If push fails:
1. Check if you're on the right branch: `git branch`
2. Pull latest changes: `git pull origin master`
3. Resolve conflicts if any
4. Push again: `git push origin master`
5. If still failing, inform user and ask for help

---

## 🔗 Additional Resources

**Essential Project Guides (in project root):**
- **DEVELOPMENT-GUIDE.md** - Tooling requirements, Docker setup, infrastructure diagnostics
- **STYLE-GUIDE.md** - File naming conventions, code style, formatting standards
- **TESTING-CHECKLIST.md** - Pre-commit checks, smoke tests, deployment validation
- **.gitignore** - Generated files policy (see comments at top)
- **C:\devop\coding_standards.md** - Comprehensive coding standards (Google Style Guides)

**Integration Guides (in `.config/`):**
- **claude-code-templates-guide.md** - Claude Code Templates (recommended for development)
- **recommended-claude-skills.md** - Claude Skills setup and workflows
- **INTEGRATIONS.md** - Complete integration guide
- **claudepro-directory-guide.md** - ClaudePro.directory reference

**Advanced Specialists:**
- **docs/advanced/SPECIALIZED-TOOLS.md** - Framework specialists, payments, AI features

**Project tracking:**
- Projects registry: `.config/projects.json`
- **Projects Database**: `C:\devop\.config\verdaio-dashboard.db` (SQLite)
  - Contains: projectId, projectName, tradeName, createdDate, status, description, templateType, projectPath, ports (frontend, backend, postgres, redis, mongo), phase percentages
  - **Update when**: Trade name is chosen, project status changes, description needs updating
  - **How to update**: Use Python script with sqlite3 module to update the project record

**Task notifications:**
- **Email notification system**: `C:\devop\scripts\` (PowerShell)
  - **Use for**: Tasks estimated to take >15 minutes
  - **Threshold**: 15 minutes
  - **Email**: chris.stephens@verdaio.com
  - **Documentation**: `C:\devop\TASK-NOTIFICATION-SYSTEM.md`

---

**Template Version:** 1.0
**Last Updated:** 2025-11-02
