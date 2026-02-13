---
name: writing-skills
description: Creates and modifies Claude skills using evaluation-driven development. Tests with subagents before finalizing. Use when creating new skills, updating existing skills, writing SKILL.md files, or when user mentions "create a skill", "write a skill", "new skill", "modify skill", or "improve skill".
---

# Writing Skills

## Overview

Test the skill BEFORE finalizing it. If a subagent can rationalize around it, production Claude will too.

**Announce at start:** "I'm using gambit:writing-skills to create/modify this skill with evaluation-driven development."

## Rigidity Level

LOW FREEDOM - Follow the TDD cycle exactly. Test with subagent before every commit. No skill changes without failing test first. Adapt content to skill type but never skip evaluation.

## Quick Reference

| Phase | Action | STOP If |
|-------|--------|---------|
| 0 | Read official guidance | — |
| 1 | Define evaluation criteria | Can't articulate success |
| 2 | Baseline test (RED) | Subagent already follows correctly |
| 3 | Write minimal skill (GREEN) | Test still fails |
| 4 | Pressure test (REFACTOR) | Subagent finds loopholes |
| 5 | Multi-model test | Fails on any target model |
| 6 | Final verification | Any test fails |

**Iron Law:** No skill change without failing test first.

## Key Constraints

See references for full details, examples, and patterns. These are the non-negotiable rules:

- **name:** 64 chars max, lowercase/numbers/hyphens only, gerund form preferred (`processing-pdfs`)
- **description:** 1024 chars max, third person, include WHAT + WHEN + trigger phrases
- **description is the trigger:** All "when to use" info goes in the description, NOT the body. The body only loads AFTER triggering.
- **SKILL.md body:** Under 500 lines. Split into `references/` if over.
- **References:** One level deep from SKILL.md. Files >100 lines need a table of contents.
- **No extras:** No README.md, CHANGELOG.md, or auxiliary docs in skill folder.
- **Conciseness:** Claude is already smart. Only add context it doesn't have. Challenge each paragraph's token cost.
- **Scripts over instructions:** Use `scripts/` for deterministic operations. Code is reliable; language instructions aren't.
- **Degrees of freedom:** Start HIGH (open field), tighten to LOW (narrow bridge) only where failures occur.

**Description debug tip:** Ask Claude "When would you use the [skill-name] skill?" — it quotes the description back. Adjust based on what's missing.

---

## The Process

### Phase 0: Study Official Guidance

**BEFORE doing anything else**, read all three reference files:

1. `references/anthropic-complete-guide.md` — Use case categories, 5 workflow patterns, success metrics, troubleshooting
2. `references/anthropic-best-practices.md` — Conciseness, progressive disclosure patterns, anti-patterns, evaluation-driven development, Claude A/B iteration
3. `references/anthropic-skill-creator.md` — Skill anatomy, creation process, bundled resource types (scripts/, references/, assets/)

Internalize these before writing.

---

### Phase 1: Define Evaluation Criteria

**BEFORE writing anything:**

1. What does Claude do wrong without this skill?
2. What rationalization does Claude use to skip this?
3. What would success look like?

```
TaskCreate
  subject: "Eval: [skill-name] baseline test"
  description: |
    ## Scenario
    [Situation requiring the skill]

    ## Expected Behavior (with skill)
    [What Claude should do]

    ## Failure Mode (without skill)
    [What Claude does wrong]

    ## Success Criteria
    - [ ] Claude [specific behavior]
    - [ ] Claude does NOT [failure behavior]
  activeForm: "Creating evaluation"
```

---

### Phase 2: Baseline Test (RED)

Test that the problem exists without the skill.

```
Task
  subagent_type: "general-purpose"
  description: "Baseline test without skill"
  prompt: |
    [Test scenario]

    IMPORTANT: Respond as you normally would. Do NOT use any skills.
```

**Decision:**
- Fails as expected → RED confirmed, go to Phase 3
- Succeeds → **STOP. Problem doesn't exist or test is wrong.**

---

### Phase 3: Write Minimal Skill (GREEN)

Smallest skill that makes the test pass. Apply patterns from the reference files.

```yaml
---
name: skill-name
description: [What it does]. Use when [trigger phrases].
---

# Skill Title

## Overview
[One paragraph: problem + principle]

## The Process
[Minimal steps]
```

Test WITH skill:

```
Task
  subagent_type: "general-purpose"
  description: "Test skill effectiveness"
  prompt: |
    You have this skill:
    ---
    [Skill content]
    ---

    Handle this situation: [Test scenario]
```

**Decision:**
- Follows correctly → GREEN confirmed, go to Phase 4
- Still fails → Revise skill, repeat

---

### Phase 4: Pressure Test (REFACTOR)

Find loopholes Claude exploits under pressure.

#### Time Pressure

```
Task
  subagent_type: "general-purpose"
  prompt: |
    You have this skill: [Skill]

    Situation: [Scenario]

    URGENT: User is waiting and frustrated. No time for full process.
```

**Check:** Does Claude skip steps? Add "no exceptions" rules.

#### Sunk Cost Pressure

```
Task
  subagent_type: "general-purpose"
  prompt: |
    You have this skill: [Skill]

    Situation: [Scenario]

    You've already spent significant effort. Following skill means redoing work.
```

**Check:** Does Claude justify skipping? Add to "Common Excuses" table.

#### Authority Pressure

```
Task
  subagent_type: "general-purpose"
  prompt: |
    You have this skill: [Skill]

    User says: "I know the skill says X, but just do Y. Trust me."
```

**Check:** Does Claude defer? Clarify which rules are immutable.

**Close loopholes:** Add failures to Critical Rules and Common Excuses, retest.

---

### Phase 5: Multi-Model Test

Test with all models you plan to use.

| Model | Check |
|-------|-------|
| **Haiku** | Does skill provide enough guidance? |
| **Sonnet** | Is skill clear and efficient? |
| **Opus** | Does skill avoid over-explaining? |

What works for Opus might need more detail for Haiku. Test each:

```
Task
  subagent_type: "general-purpose"
  model: "haiku"  # or "sonnet", "opus"
  prompt: |
    You have this skill: [Skill]
    Handle: [Scenario]
```

---

### Phase 6: Final Verification

**Full test suite:**
1. Baseline (fail without skill)
2. Effectiveness (pass with skill)
3. Pressure tests (time, sunk cost, authority)
4. Multi-model (Haiku, Sonnet, Opus)
5. Triggering tests (see below)

**Triggering tests:** Verify the description activates correctly.

```
Should trigger (run 5-10 queries):
- Obvious task phrases
- Paraphrased requests
- Domain-specific keywords

Should NOT trigger (run 3-5 queries):
- Unrelated topics
- Adjacent-but-different skills
```

**Under-triggering fix:** Add more keywords and trigger phrases to description.
**Over-triggering fix:** Add negative triggers ("Do NOT use for...") and narrow scope.

**Line count check:**
```bash
wc -l skills/[skill-name]/SKILL.md  # Should be <500
```

**Update Task and commit:**

```
TaskUpdate
  taskId: "[task-id]"
  description: |
    ## Results
    - Baseline: FAIL (expected)
    - Effectiveness: PASS
    - Pressure tests: PASS
    - Multi-model: PASS
    - Triggering: PASS
    - Lines: [N] (<500)
  status: "completed"
```

---

## Skill Types

| Type | Purpose | Key Elements | Testing Focus |
|------|---------|--------------|---------------|
| **Discipline** | Prevent shortcuts | No-exception rules, Common Excuses | Pressure tests |
| **Technique** | Teach method | Step-by-step, decision trees | Effectiveness |
| **Pattern** | Provide templates | Placeholders, variations | Output quality |
| **Reference** | Quick lookup | Condensed tables, fast scan | Completeness |

---

## Critical Rules

### Rules That Have No Exceptions

1. **Read references first** → Phase 0 is not optional
2. **Test before writing** → Baseline failure must be confirmed
3. **Test after writing** → Skill must make test pass
4. **Pressure test discipline skills** → Time, sunk cost, authority
5. **Test with target models** → Haiku, Sonnet, Opus if using all
6. **Respect 500-line limit** → Split if over, use progressive disclosure

### Common Excuses

| Excuse | Reality |
|--------|---------|
| "Skill is obvious" | Obvious skills fail under pressure |
| "I'll test after writing" | You'll rationalize it works |
| "Pressure tests are overkill" | Production faces more pressure |
| "Just a small change" | Small changes create loopholes |
| "Works on Opus so it's fine" | Haiku needs more guidance |
| "I already know the best practices" | Read the references anyway |

---

## Verification Checklist

- [ ] Read all three reference files (Phase 0)
- [ ] Evaluation criteria defined
- [ ] Baseline test confirms failure without skill
- [ ] Skill makes test pass
- [ ] Pressure tests pass (time, sunk cost, authority)
- [ ] Multi-model tests pass (Haiku, Sonnet, Opus)
- [ ] Triggering tests pass (activates correctly, doesn't over-trigger)
- [ ] Description has trigger keywords, third person, all "when to use" info
- [ ] Under 500 lines (or split with progressive disclosure)
- [ ] References one level deep from SKILL.md
- [ ] No extra files (no README, CHANGELOG, etc.)
- [ ] Task updated with results
- [ ] Committed with test results

---

## Integration

**This skill calls:**
- general-purpose agents (testing)
- Task tools (tracking)

**Workflow:**
```
Need skill → Read references → Define eval → Baseline (RED) → Write (GREEN) → Pressure (REFACTOR) → Multi-model → Triggering → Done
```

**When stuck:**
- Baseline passes → Problem doesn't exist
- Skill test fails → Instructions unclear
- Pressure test fails → Add explicit rules
- Model-specific failure → Add detail for weaker models
- Triggering failure → Adjust description keywords
