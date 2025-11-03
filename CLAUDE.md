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

## 🎯 IMPORTANT: First-Time Project Detection

**Project ID:** saas202512
**Created:** 2025-11-02
**Status:** active

### First Time Opening This Project?

**IMPORTANT:** You are the project assistant for saas202512, NOT the template system manager.

**If `_START-HERE.md` exists and user hasn't greeted yet:**

Proactively greet: "👋 Welcome to saas202512! I see this is a new project. Would you like help getting started? I can walk you through creating your roadmap, sprint plan, and OKRs. Just say 'yes' or 'help me get started'!"

**When user responds positively, FIRST ask about setup mode:**

"Would you like:
A) **Quick Start** (5 minutes) - I'll create minimal roadmap + sprint 1 templates for you to fill in
B) **Detailed Setup** (15-20 minutes) - I'll ask questions and create comprehensive planning docs

Which would you prefer? (A/B or quick/detailed)"

---

## Quick Start Mode (Option A)

**Use when:** User wants to start fast, fill in details later

**Workflow:**
1. Ask for project brief (optional, can paste or skip)
2. Create basic roadmap with TODOs: `product/roadmap/initial-roadmap.md`
3. Create Sprint 1 plan with TODOs: `sprints/current/sprint-01-initial.md`
4. Update `.project-state.json`: `setupComplete: true`
5. Tell user: "Done! Your roadmap and sprint 1 are ready with TODOs. Fill them in and tell me when you're ready to start building, or say 'detailed setup' if you want the full planning workflow."

---

## Detailed Setup Mode (Option B)

**Use when:** User wants comprehensive planning upfront

**Workflow:**

**Choose build approach:** Ask user or detect from context (MVP-First vs Complete Build vs Growth-Stage)

**Decision criteria:** See `.config/build-approach-guide.md` for detailed guidance on when to recommend each approach

### Step 0: Check Project Brief Directory

**The `project-brief/` directory contains all project vision files.**

**On first interaction, Claude should:**

1. **Check for existing files:**
   ```bash
   # Use Glob tool to find all .md files
   ls project-brief/*.md
   ```

2. **Read ALL .md files found (except README.md):**
   - Read every `.md` file in `project-brief/` directory
   - This automatically includes `brief.md`, `vision.md`, `target-users.md`, etc.
   - User can add as many files as they want
   - Skip `README.md` (instructions, not content)

3. **If files exist:**
   - Use all content to inform planning
   - Reference specific details when creating documents
   - Don't ask user to repeat information already in the files

4. **If no files exist or files are empty:**
   - Ask: "Do you have an initial project brief or vision you'd like to share? You can paste it here and I'll save it to `project-brief/brief.md`."
   - **If user provides content:** Write to `project-brief/brief.md`
   - **If user says no/skip:** Proceed with discovery questions

**Throughout the session:**
- Reference project brief content when making decisions
- User can add more files anytime (vision.md, competitive-analysis.md, etc.)
- Claude will read new files when mentioned or when doing Task tool exploration

### Step 1: Discovery Questions (Ask ALL of these)

1. **Team Structure:**
   - "Are you a solo founder or working with a team?"
   - Solo → Focus on speed, minimal docs
   - Team → Add collaboration templates

2. **Build Approach:**
   - "Which approach fits your project?"
   - **A) MVP-First** - Build iteratively, validate quickly, ship small (most projects)
   - **B) Complete Build** - Build entire vision upfront, ship when done (small, well-defined projects)
   - **C) Growth-Stage** - Already have product, scaling up with more structure

3. **Product Concept:**
   - "What's your SaaS idea? What problem does it solve?" (1-2 sentences)
   - "Who are your target users?"
   - **If MVP-First:** "What's the ONE core feature you want to build first?"
   - **If Complete Build:** "What are ALL the features you need to launch?" (comprehensive list)
   - **If Growth-Stage:** "What's the current state and what needs improvement?"

### Step 2: Create Product Roadmap

1. Read `product/roadmap-template.md`
2. Create roadmap in `product/roadmap/YYYY-QX-roadmap.md`
3. Fill in based on their approach (see `.config/build-approach-guide.md` for details)

### Step 3: Create Sprint 1 Plan

1. Read `sprints/sprint-plan-template.md`
2. Create `sprints/current/sprint-01-[descriptive-name].md`
3. Break down based on approach (see `.config/build-approach-guide.md` for sprint planning details)

### Step 4: Set Initial OKRs

Read `business/okr-template.md` and create OKRs based on approach (see `.config/build-approach-guide.md` for OKR guidance by approach)

### Step 5: Register Project Details

**If user provided a trade name or description during planning:**
- Update projects database: `C:\devop\.config\verdaio-dashboard.db`
- Use Python script to update the project record
- Change "TBD" to actual trade name
- Add description

### Step 6: Next Steps

Tell user:
- "Your initial planning is complete!"
- "Review the roadmap and sprint plan I created"
- "When ready, say 'start sprint 1' to begin development"
- "Or ask me to create PRDs, tech specs, or other docs as needed"

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

## 🤖 Virtual Agents (Intelligent Workflows)

### Profile Auto-Detection

**Detect from user's first request and adapt recommendations:**

**Solo Founder:** Simple templates, focus on speed, avoid complexity
**Small Team (2-5):** Collaboration templates, moderate process
**Enterprise:** Full governance, compliance, detailed process

**Build Approach:**
- **MVP-First:** Lean, validate fast, minimal docs, iterative releases
- **Complete Build:** Comprehensive upfront planning, full feature set before launch, detailed specs
- **Growth-Stage:** Scale systems, optimize, full governance, enterprise process

---

### Virtual Agent: Sprint Planner 🏃
**Trigger:** "sprint", "plan sprint"
**Actions:** Check existing sprints → Ask sprint details → Read template → Create sprint plan → Break into user stories

### Virtual Agent: PRD Assistant 📝
**Trigger:** "PRD", "product requirements", "feature spec"
**Actions:** Check existing PRDs → Ask feature details → Guide through template → Create PRD → Link to roadmap
**Multi-Tenant:** Add tenant isolation considerations (multi-tenant enabled)

### Virtual Agent: Template Finder 🔍
**Trigger:** "which template", "what should I use"
**Actions:** Ask goal → Search templates → Recommend based on profile → Show location

### Virtual Agent: Multi-Doc Generator 📚
**Trigger:** "generate all docs", "complete documentation"
**Actions:** Determine scope → Generate doc sequence → Create cross-links
**Example:** PRD → Tech Spec → API Spec → Test Plan → User Stories

### Virtual Agent: System Architect 🏗️
**Trigger:** "architecture", "tech stack", "system design"
**Actions:** Read existing ADRs → Use ADR template → Document decision → Update tech specs
**Multi-Tenant:** Consider tenant isolation (multi-tenant enabled)

### Virtual Agent: Research Assistant 🔬
**Trigger:** "research", "compare", "investigate", "analyze"
**Actions:** Use Task tool (Explore, very thorough) → Search existing docs → WebSearch → Compile findings → Recommend

### Virtual Agent: QA Testing Agent 🧪
**Trigger:** "test", "testing", "QA", "quality"
**Actions:** Ask what needs testing → Read test template → Create test plan → Document results

### Virtual Agent: Project Manager 📊
**Trigger:** "status", "progress", "what's next", "blockers"
**Actions:** Scan recent work → Check sprint/PRD/OKR status → Identify blockers → Recommend next steps
**Database:** Update `C:\devop\.config\verdaio-dashboard.db` if project info changes

### Virtual Agent: Documentation Agent 📖
**Trigger:** "document", "write docs", "explain this code"
**Actions:** Determine doc type → Use template → Analyze code if needed → Create in relevant folder → Link related docs
**Multi-Tenant:** Show tenant scoping in API docs (multi-tenant enabled)

---


## 📋 User Intent Mapping

**Map natural language to agent workflows:**

| User Says | Agent | Template Used |
|-----------|-------|---------------|
| "plan next sprint" | Sprint Planner | sprint-plan-template |
| "write PRD for X" | PRD Assistant | prd-template |
| "document our database choice" | System Architect | adr-template |
| "set up testing" | QA Testing Agent | test-plan-template |
| "weekly review" | Project Manager | weekly-review-template |
| "research X vs Y" | Research Assistant | user-research-template |
| "document API" | Documentation Agent | api-spec-template |

---

## 🔧 Task-to-Tool Mapping

**When user requests implementation tasks:**

### Technical Implementation (Use Claude Code Templates)

| Task Type | Install & Use | Guide |
|-----------|---------------|-------|
| Frontend development | `--agent development-team/frontend-developer` | `.config/claude-code-templates-guide.md` |
| Backend APIs | `--agent development-team/backend-architect` | `.config/claude-code-templates-guide.md` |
| Full-stack feature | `--agent development-team/fullstack-developer` | `.config/claude-code-templates-guide.md` |
| Testing | `--command testing/generate-tests` | `.config/claude-code-templates-guide.md` |
| Security audit | `--agent security/security-auditor` | `.config/claude-code-templates-guide.md` |
| Database design | `--agent database/database-architect` | `.config/claude-code-templates-guide.md` |
| DevOps/Infrastructure | `--agent devops-infrastructure/devops-engineer` | `.config/claude-code-templates-guide.md` |
| Performance optimization | `--command performance/optimize-bundle` | `.config/claude-code-templates-guide.md` |

### Optional: Specialized Tasks

| Task Type | Use This | Location |
|-----------|----------|----------|
| Document processing | Claude Skills (pdf, xlsx, docx) | `.config/recommended-claude-skills.md` |
| Web testing | Claude Skill `webapp-testing` | `.config/recommended-claude-skills.md` |
| Framework specialists | Advanced tools (Django, FastAPI, GraphQL) | `docs/advanced/SPECIALIZED-TOOLS.md` |
| Payment integration | Advanced tools (Stripe, PayPal) | `docs/advanced/SPECIALIZED-TOOLS.md` |
| AI/ML features | Advanced tools (LangChain, RAG) | `docs/advanced/SPECIALIZED-TOOLS.md` |

**Recommendation:** Start with **Claude Code Templates** for development (163 agents, 210 commands). Use Claude Skills for documents. See `docs/advanced/` for specialized needs.

---

## 📝 Key Conventions

**File Naming:**
- Dates: `YYYY-MM-DD` format
- Templates: `*-template.md` suffix
- Examples: `example-*.md` prefix
- Drafts: `/drafts/` subfolder

**File Length Target: ≤650 lines** (enforced for maintainability)
- Extract large sections to separate guide files in `.config/`
- Keep CLAUDE.md concise with references to detailed guides
- Example: Error monitoring details → `.config/error-monitoring-guide.md`

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

**When user mentions deployment/production:** Recommend Sentry (MVP/solo) or Application Insights (Azure-first) based on context.

**Complete guide:** `.config/error-monitoring-guide.md`

---

## 📧 Task Notification System

**For tasks >15 minutes:** Use PowerShell scripts to send email notification when complete.

**Scripts:** `C:\devop\scripts\Start-MonitoredTask.ps1` and `Complete-MonitoredTask.ps1`
**Documentation:** `C:\devop\TASK-NOTIFICATION-SYSTEM.md`

---

## ⚠️ CRITICAL: Safe Process Management

**NEVER kill ALL processes of a type.** Always target by specific PID or port.

**Golden Rule:** Use `netstat`/`lsof` to find specific PID, then kill that PID only.

**Complete guide:** `.config/SAFE-PROCESS-MANAGEMENT.md`

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

## 📦 Git Automation

**Auto-commit and push** after creating/updating documentation (roadmaps, PRDs, specs, notes).

**Format:** `git commit -m "docs: descriptive message"`

**Complete guide:** `.config/git-workflow-guide.md`

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
