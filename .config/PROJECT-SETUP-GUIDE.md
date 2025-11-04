# Project Setup Guide

**For:** saas202512 (Pet Care)
**Multi-tenant:** Enabled (subdomain model)

This guide covers initial project setup workflows for new projects.

---

## 🎯 First-Time Project Detection

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

### Build Approach Guide (for Claude to reference)

**When to recommend MVP-First:**
- User is uncertain about product-market fit
- Testing a new market or idea
- Complex product with many unknowns
- Want to validate with real users quickly
- Budget or time constraints require iterative approach
- **Most projects should use this approach**

**When to recommend Complete Build:**
- Small, well-defined project with clear scope
- Replicating existing product/workflow (migration project)
- Internal tool with known requirements
- All features are essential for launch (not optional)
- User has validated the concept already
- Timeline: 4-8 weeks total (not multi-month projects)
- **Example:** "Build a simple invoice generator with PDF export, email sending, and client management"

**When to recommend Growth-Stage:**
- Product is already live with users
- Shifting from ad-hoc to structured development
- Scaling team or infrastructure
- Adding governance and process

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

After gathering answers:
1. Read `product/roadmap-template.md`
2. Create roadmap in `product/roadmap/YYYY-QX-roadmap.md`
3. Fill in based on their approach:

**If MVP-First:**
   - Product vision (their problem/solution)
   - Strategic themes (MVP focus, iterative releases)
   - Now/Next/Later breakdown (prioritize the ONE core feature)
   - Success metrics (validation-focused)
   - Timeline: Phased releases (Sprint 1 → v0.1 → v1.0)

**If Complete Build:**
   - Product vision (complete scope upfront)
   - Feature breakdown (ALL features organized by module)
   - Single comprehensive release plan
   - Success metrics (launch-focused)
   - Timeline: Build complete → Test → Launch
   - Note: "This is a complete build approach. All features will be built before launch."

**If Growth-Stage:**
   - Current state assessment
   - Strategic themes (scale, optimize, improve)
   - Prioritized improvements
   - Success metrics (growth and efficiency)

### Step 3: Create Sprint 1 Plan

1. Read `sprints/sprint-plan-template.md`
2. Create `sprints/current/sprint-01-[descriptive-name].md`
3. Break down based on approach:

**If MVP-First:**
   - High priority: Foundation + ONE core feature only
   - Medium priority: Supporting features for core
   - Low priority: Nice-to-haves
   - Estimate: ~2 weeks for solo, ~1 week for teams
   - Goal: Ship smallest viable version

**If Complete Build:**
   - Organize ALL features into logical build sequence
   - Create multiple sprint plans (sprint-01, sprint-02, sprint-03, etc.)
   - Each sprint = one complete module or feature set
   - High priority: Core infrastructure + essential features
   - Medium priority: Secondary features
   - Low priority: Polish and optimization
   - Estimate: Total timeline based on scope (typically 4-8 weeks for "small" complete builds)
   - Goal: Build entire product before launch

**If Growth-Stage:**
   - High priority: Critical improvements and scaling work
   - Medium priority: Technical debt and optimization
   - Low priority: New features
   - Estimate: Standard sprint cadence (1-2 weeks)

### Step 4: Set Initial OKRs

**If MVP-First (solo):** Skip or make very simple (1-2 objectives focused on validation)

**If MVP-First (team):**
   - Read `business/okr-template.md` and create quarterly OKRs
   - Focus on: Launch, users, validation metrics

**If Complete Build:**
   - Create comprehensive OKRs covering the full build timeline
   - Focus on: Completion milestones, quality metrics, launch readiness
   - Example objectives: "Ship all core features by Week 6", "Achieve 95% test coverage", "Complete beta testing with 10 users"

**If Growth-Stage:**
   - Full quarterly OKRs required
   - Focus on: Growth, efficiency, scale metrics

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

## Profile Auto-Detection

**Detect from user's first request and adapt recommendations:**

**Solo Founder:** Simple templates, focus on speed, avoid complexity
**Small Team (2-5):** Collaboration templates, moderate process
**Enterprise:** Full governance, compliance, detailed process

**Build Approach:**
- **MVP-First:** Lean, validate fast, minimal docs, iterative releases
- **Complete Build:** Comprehensive upfront planning, full feature set before launch, detailed specs
- **Growth-Stage:** Scale systems, optimize, full governance, enterprise process

---

**Guide Version:** 1.0
**Last Updated:** 2025-11-04
