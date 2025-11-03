# Build Approach Guide

**Use this guide to recommend the right build approach based on user context.**

---

## When to Recommend MVP-First

**Characteristics:**
- User is uncertain about product-market fit
- Testing a new market or idea
- Complex product with many unknowns
- Want to validate with real users quickly
- Budget or time constraints require iterative approach
- **Most projects should use this approach**

**Planning approach:**
- Lean documentation (roadmap + Sprint 1)
- Focus on ONE core feature
- Iterative releases (Sprint 1 → v0.1 → v1.0)
- Validation-focused metrics
- Encourage speed over perfection

---

## When to Recommend Complete Build

**Characteristics:**
- Small, well-defined project with clear scope
- Replicating existing product/workflow (migration project)
- Internal tool with known requirements
- All features are essential for launch (not optional)
- User has validated the concept already
- Timeline: 4-8 weeks total (not multi-month projects)

**Example:** "Build a simple invoice generator with PDF export, email sending, and client management"

**Planning approach:**
- Comprehensive upfront planning
- Document ALL features before starting
- Multiple sprint plans (sprint-01, sprint-02, etc.)
- Single comprehensive release
- Launch-focused metrics
- Quality and completeness emphasis

---

## When to Recommend Growth-Stage

**Characteristics:**
- Product is already live with users
- Shifting from ad-hoc to structured development
- Scaling team or infrastructure
- Adding governance and process

**Planning approach:**
- Full quarterly OKRs
- Current state assessment
- Prioritized improvements roadmap
- Growth and efficiency metrics
- Balance planning with execution

---

## Sprint Planning by Approach

### MVP-First Sprint Planning

**Sprint 1 focus:**
- High priority: Foundation + ONE core feature only
- Medium priority: Supporting features for core
- Low priority: Nice-to-haves
- Estimate: ~2 weeks for solo, ~1 week for teams
- Goal: Ship smallest viable version

**Subsequent sprints:**
- Iterative feature additions based on user feedback
- Each sprint validates one hypothesis
- Quick releases (1-2 week cycles)

### Complete Build Sprint Planning

**Sprint sequence:**
- Create multiple sprint plans upfront (sprint-01, sprint-02, sprint-03, etc.)
- Each sprint = one complete module or feature set
- High priority: Core infrastructure + essential features
- Medium priority: Secondary features
- Low priority: Polish and optimization
- Estimate: Total timeline based on scope (typically 4-8 weeks)
- Goal: Build entire product before launch

**Key difference:** All features documented and sequenced upfront

### Growth-Stage Sprint Planning

**Standard cadence:**
- High priority: Critical improvements and scaling work
- Medium priority: Technical debt and optimization
- Low priority: New features
- Estimate: Standard 1-2 week sprints
- Goal: Continuous improvement and scale

---

## OKRs by Approach

### MVP-First OKRs

**Solo founder:**
- Skip or keep very simple (1-2 objectives)
- Focus on validation metrics
- Example: "Launch v0.1 with 10 test users by end of sprint 2"

**Small team:**
- Quarterly OKRs focused on launch and validation
- Objectives: Launch, users, validation metrics
- Example: "Acquire 100 early users with 40% weekly retention"

### Complete Build OKRs

**Requirements:**
- Comprehensive OKRs covering full build timeline
- Focus on completion milestones, quality, launch readiness
- Example objectives:
  - "Ship all core features by Week 6"
  - "Achieve 95% test coverage"
  - "Complete beta testing with 10 users"

### Growth-Stage OKRs

**Requirements:**
- Full quarterly OKRs
- Focus on growth, efficiency, scale metrics
- Example: "Increase MAU by 30% while reducing churn to <5%"

---

## Detecting User's Approach

**Ask directly:**
> "Which approach fits your project?"
> - **A) MVP-First** - Build iteratively, validate quickly, ship small (most projects)
> - **B) Complete Build** - Build entire vision upfront, ship when done (small, well-defined projects)
> - **C) Growth-Stage** - Already have product, scaling up with more structure

**Or detect from context:**

**Signals for MVP-First:**
- "I want to test if people will use it"
- "I'm not sure about product-market fit yet"
- "I want to launch quickly"
- "What's the minimum we need to build?"
- New startup, no users yet

**Signals for Complete Build:**
- "I know exactly what I need to build"
- "This is an internal tool for our team"
- "We're migrating from X to Y"
- "All these features are required at launch"
- Clear, fixed requirements

**Signals for Growth-Stage:**
- "We already have users"
- "We need better processes"
- "We're scaling the team"
- "Our codebase is a mess"
- Product already in production

---

## Common Mistakes to Avoid

### Don't Recommend MVP-First When:
- User has clear, fixed requirements
- Small, well-defined scope (can ship complete in 4-8 weeks)
- Replicating existing tool with known workflow

### Don't Recommend Complete Build When:
- User is uncertain about requirements
- Testing new market or unvalidated idea
- Timeline >2 months
- Many unknowns or assumptions to validate

### Don't Recommend Growth-Stage When:
- No product in production yet
- No current users
- Still in planning/design phase

---

## Summary Table

| Approach | Timeline | Planning | Focus | Best For |
|----------|----------|----------|-------|----------|
| **MVP-First** | Iterative (2-week sprints) | Minimal docs | Validation | Most new projects |
| **Complete Build** | 4-8 weeks total | Comprehensive upfront | Completion | Small, clear scope |
| **Growth-Stage** | Ongoing sprints | Full governance | Scaling | Existing products |
