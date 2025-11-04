# Virtual Agents Guide

**For:** saas202512 (Pet Care)
**Multi-tenant:** Enabled (subdomain model)

This guide documents all virtual agent workflows and their triggers.

---

## 🤖 What are Virtual Agents?

Virtual agents are intelligent workflows that Claude uses to handle specific types of tasks. They combine:
- Task detection (trigger phrases)
- Specialized workflows
- Template usage
- Tool delegation

**Key principle:** Virtual agents do the planning and documentation. For technical implementation, use Claude Code Templates.

---

## Virtual Agent: Sprint Planner 🏃

**Trigger:** User mentions "sprint", "plan sprint", "create sprint"

**Workflow:**
1. Use Task tool (subagent_type=Explore) to check existing sprints
2. Ask: sprint number, duration, goals
3. Read `sprints/sprint-plan-template.md`
4. Create new sprint plan in `sprints/current/`
5. Break goals into user stories
6. Link to product roadmap and OKRs

**Delegation:** For technical implementation → Use Claude Code Templates (fullstack-developer)

---

## Virtual Agent: PRD Assistant 📝

**Trigger:** User mentions "PRD", "product requirements", "feature spec"

**Workflow:**
1. Use Task tool (subagent_type=Explore) to check existing PRDs
2. Ask: feature name, target users, problem to solve
3. Read `product/prd-template.md`
4. Guide through sections (Problem, Solution, Success Metrics)
5. **If multi-tenant (true):** Add multi-tenant considerations section
6. Create PRD in `product/PRDs/`
7. Link to roadmap and relevant sprints

**Multi-Tenant Reminder:** Ask about tenant isolation, cross-tenant access, tenant-specific features

**Delegation:** For API design → Use Claude Code Templates (backend-architect)

---

## Virtual Agent: Template Finder 🔍

**Trigger:** User asks "which template", "what should I use", "help me find"

**Workflow:**
1. Ask about their goal
2. Use Task tool (subagent_type=Explore) to search templates
3. Recommend based on profile and phase
4. Show template location and offer to walk through it

**Template priorities by profile:**
- **Solo:** Sprint plan, PRD, Weekly review
- **Team:** Add: Retrospective, Meeting notes, Tech specs
- **Enterprise:** Add: ADRs, API specs, Incident postmortems

---

## Virtual Agent: Multi-Doc Generator 📚

**Trigger:** User says "generate all docs", "complete documentation", "full set"

**Workflow:**
1. Ask: What's being documented? (feature, sprint, system)
2. Determine required docs based on scope
3. Generate in sequence, each referencing others
4. Create cross-links between related docs

**Example - New feature:**
- PRD → Tech Spec → API Spec → Test Plan → User Stories

---

## Virtual Agent: System Architect 🏗️

**Trigger:** User mentions "architecture", "tech stack", "system design"

**Workflow:**
1. Ask: What are you designing?
2. Read existing `technical/adr/` for context
3. Use `technical/adr-template.md` for decisions
4. **If multi-tenant (true):** Reference `technical/multi-tenant-architecture.md` and ensure tenant isolation is considered
5. Create ADR documenting choice and alternatives
6. Update tech specs if needed

**Multi-Tenant Reminder:** Always consider tenant data isolation, performance per tenant, and compliance

**Delegation:** For implementation → Use Claude Code Templates specialized agents

---

## Virtual Agent: Research Assistant 🔬

**Trigger:** User mentions "research", "compare", "investigate", "analyze"

**Workflow:**
1. Use Task tool (subagent_type=Explore, thoroughness=very thorough)
2. Search existing docs for prior research
3. Use WebSearch for external information
4. Compile findings in `product/research/` or `technical/research/`
5. Provide recommendation with trade-offs

**Delegation:** For technical deep-dives → Use Claude Code Templates or docs/advanced/ specialists

---

## Virtual Agent: QA Testing Agent 🧪

**Trigger:** User mentions "test", "testing", "QA", "quality"

**Workflow:**
1. Ask: What needs testing?
2. Read `technical/testing/test-plan-template.md`
3. Create test plan and test cases
4. Use webapp-testing skill for browser tests (if installed)
5. Document results

**Delegation:** For test automation → Use Claude Code Templates (test generation)

---

## Virtual Agent: Project Manager 📊

**Trigger:** User asks about "status", "progress", "what's next", "blockers"

**Workflow:**
1. Use Task tool (subagent_type=Explore) to scan recent work
2. Check: sprint status, PRD completion, OKR progress
3. Identify: completed items, in-progress, blockers
4. Recommend next steps based on roadmap
5. Offer to update weekly review
6. **If project info changes** (trade name chosen, status, description) → Update projects database

**Projects Database:** `C:\devop\.config\verdaio-dashboard.db` (SQLite)
**Use Python script** with sqlite3 module to update the project record

**Delegation:** For task tracking → User can choose their preferred tool (Trello, Asana, Notion, etc.).

---

## Virtual Agent: Documentation Agent 📖

**Trigger:** User says "document", "write docs", "explain this code"

**Workflow:**
1. Determine doc type (API, runbook, process, architecture)
2. Use appropriate template
3. For code docs: analyze code structure first
4. **If multi-tenant (true):** Ensure API docs show tenant scoping in examples
5. Create in relevant folder (technical/, workflows/)
6. Link to related docs

**Multi-Tenant Reminder:** API documentation should show how endpoints are tenant-scoped

**Delegation:** For API docs → Use Claude Code Templates (backend-architect)

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

**Guide Version:** 1.0
**Last Updated:** 2025-11-04
