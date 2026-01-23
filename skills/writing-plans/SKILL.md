---
name: writing-plans
description: Use when you have requirements for a multi-step task - creates Tasks with dependencies, exact file paths, complete code, verification commands
---

# Writing Plans

## Overview

Create comprehensive implementation plans as native Claude Code Tasks. Assume the engineer has zero codebase context and questionable taste. Document everything: exact file paths, complete code, verification commands, expected output.

**Core principle:** No placeholders. No assumptions. Verify with codebase-investigator, then write definitive steps.

**Announce at start:** "I'm using gambit:write-plan to create the implementation plan."

## Rigidity Level

MEDIUM FREEDOM — Follow task structure and verification pattern strictly. Adapt implementation details to actual codebase state.

## Quick Reference

| Step | Action | Critical Rule |
|------|--------|---------------|
| **Create Epic** | TaskCreate with requirements + success criteria | Requirements are IMMUTABLE |
| **Verify Codebase** | Use codebase-investigator agent | NEVER verify yourself |
| **Create Subtasks** | TaskCreate with dependencies | Bite-sized (2-5 min each) |
| **Present to User** | Show COMPLETE plan FIRST | Then ask for approval |
| **Continue** | Move to next subtask automatically | NO asking permission between |

**FORBIDDEN:** Placeholders like `[implementation details go here]`
**REQUIRED:** Complete code, exact paths, real commands

## When to Use

After `gambit:brainstorm` produces approved requirements, or when user provides clear spec.

Symptoms:
- Have requirements, need implementation plan
- Need to break work into trackable pieces
- Want explicit file paths and code examples
- Multiple engineers or sessions will execute

## The Process

### 1. Create Epic Task

The epic contains immutable requirements — these don't change during implementation.

```
TaskCreate:
  subject: "Feature: [Name]"
  description: |
    ## Goal
    [One sentence]

    ## Requirements (IMMUTABLE)
    - [Requirement 1]
    - [Requirement 2]

    ## Success Criteria
    - [ ] [Criterion 1]
    - [ ] [Criterion 2]

    ## Architecture
    [2-3 sentences about approach]

    ## Anti-patterns (FORBIDDEN)
    - [What NOT to do]
```

### 2. Verify Codebase State

**CRITICAL: Use codebase-investigator agent. Never verify yourself.**

Dispatch agent with assumptions from requirements:

```
Assumptions from requirements:
- Auth service should be in src/services/auth.ts
- User model in src/models/user.ts with email field
- Tests at tests/services/auth.test.ts

Verify:
1. What exists vs what we expect
2. Structural differences (paths, exports, signatures)
3. Dependency versions
4. Related code we should know about
```

**Based on report:**
- ✓ Confirmed → Use in plan
- ✗ Incorrect → Adjust plan to reality
- + Found additional → Incorporate

**NEVER write conditional steps:**
- ❌ "Update `index.js` if exists"
- ❌ "Modify `config.py` (if present)"

**ALWAYS write definitive steps:**
- ✅ "Create `src/auth.ts`" (investigator confirmed doesn't exist)
- ✅ "Modify `src/index.ts:45-67`" (investigator confirmed location)

### 3. Create Subtasks with Dependencies

Each subtask is bite-sized (2-5 minutes) and follows TDD:

```
TaskCreate:
  subject: "Add login function"
  description: |
    **Files:**
    - Create: `src/services/auth.ts`
    - Test: `tests/services/auth.test.ts`

    **Step 1: Write failing test**
    ```typescript
    // tests/services/auth.test.ts
    import { login } from '../src/services/auth';

    describe('login', () => {
      it('returns user on valid credentials', async () => {
        const result = await login('test@example.com', 'password123');
        expect(result.success).toBe(true);
        expect(result.userId).toBeDefined();
      });
    });
    ```

    **Step 2: Run test (expect fail)**
    ```bash
    npm test -- tests/services/auth.test.ts
    # Expected: Cannot find module '../src/services/auth'
    ```

    **Step 3: Implement minimal code**
    ```typescript
    // src/services/auth.ts
    export interface LoginResult {
      success: boolean;
      userId?: string;
    }

    export async function login(email: string, password: string): Promise<LoginResult> {
      // Minimal implementation to pass test
      return { success: true, userId: '1' };
    }
    ```

    **Step 4: Run test (expect pass)**
    ```bash
    npm test -- tests/services/auth.test.ts
    # Expected: PASS
    ```

    **Step 5: Commit**
    ```bash
    git add src/services/auth.ts tests/services/auth.test.ts
    git commit -m "feat(auth): add login function"
    ```
```

**Set dependencies:**
```
TaskUpdate:
  taskId: [subtask-2-id]
  addBlockedBy: [subtask-1-id]
```

### 4. Present Complete Plan

Show the FULL plan before asking for approval:

```
## Epic: [Name]

### Task 1: [Title]
[Full description with all steps, code, commands]

### Task 2: [Title] (blocked by Task 1)
[Full description...]

### Task 3: [Title] (blocked by Task 2)
[Full description...]

---

**Codebase verification findings:**
- ✓ Confirmed: [what matched]
- ✗ Adjusted: [what changed from assumptions]
- + Discovered: [relevant findings]
```

**THEN ask:**
"Is this plan approved? I can begin execution with gambit:execute-plan."

### 5. Continue Automatically

After user approves:
- All Tasks are created with dependencies
- Ready for `gambit:execute-plan`

**Don't ask:** "Should I continue?" or "What next?"
**Just report:** "Plan created. N tasks ready for execution."

## Task Granularity

**Each step is ONE action (2-5 minutes):**

1. "Write the failing test" — one step
2. "Run it to verify it fails" — one step
3. "Implement minimal code to pass" — one step
4. "Run tests to verify they pass" — one step
5. "Commit" — one step

**NOT:**
- "Implement authentication" (too big)
- "Add tests" (too vague)
- "Update the code" (meaningless)

## Examples

### Bad: Placeholder Content

```
TaskCreate:
  subject: "Implement auth"
  description: |
    Add authentication to the app.

    [See requirements for details]
    [Implementation steps will be added]
```

**Why it fails:** Zero-context engineer can't execute this.

### Good: Complete Content

```
TaskCreate:
  subject: "Add password hashing to user registration"
  description: |
    **Files:**
    - Modify: `src/services/user.ts:23-45`
    - Test: `tests/services/user.test.ts`

    **Step 1: Write failing test**
    ```typescript
    it('hashes password before storing', async () => {
      const user = await createUser('test@example.com', 'plaintext');
      expect(user.password).not.toBe('plaintext');
      expect(user.password).toMatch(/^\$2[ayb]\$.{56}$/); // bcrypt format
    });
    ```

    **Step 2: Run test (expect fail)**
    ```bash
    npm test -- tests/services/user.test.ts -t "hashes password"
    # Expected: FAIL - password equals 'plaintext'
    ```

    **Step 3: Add bcrypt hashing**
    ```typescript
    // src/services/user.ts line 23-45
    import bcrypt from 'bcrypt';

    export async function createUser(email: string, password: string) {
      const hashedPassword = await bcrypt.hash(password, 10);
      return db.users.create({
        email,
        password: hashedPassword,
      });
    }
    ```

    **Step 4: Run test (expect pass)**
    ```bash
    npm test -- tests/services/user.test.ts -t "hashes password"
    # Expected: PASS
    ```

    **Step 5: Commit**
    ```bash
    git add src/services/user.ts tests/services/user.test.ts
    git commit -m "feat(user): hash passwords with bcrypt"
    ```
```

## Anti-patterns

**Don't:**
- Write placeholders ("details above", "see requirements")
- Verify codebase yourself (use codebase-investigator)
- Write conditional steps ("if exists")
- Ask permission between subtasks
- Create vague tasks ("implement feature")

**Do:**
- Write complete code in every step
- Use codebase-investigator to verify assumptions
- Write definitive steps based on verification
- Continue automatically after approval
- Create bite-sized tasks (2-5 min each)

## Verification Checklist

Before presenting plan:
- [ ] Used codebase-investigator (not manual verification)
- [ ] All steps have complete code (no placeholders)
- [ ] All steps have exact file paths
- [ ] All steps have exact commands with expected output
- [ ] Dependencies set correctly between tasks
- [ ] Each task is 2-5 minutes of work

## Integration

**This skill is called by:**
- `gambit:brainstorm` (after design approval)
- User via `/gambit:write-plan`

**This skill calls:**
- codebase-investigator agent (verify assumptions)
- `gambit:execute-plan` (offered after plan approval)

**Task tools used:**
- `TaskCreate` — Create epic and subtasks
- `TaskUpdate` — Set dependencies via `addBlockedBy`
- `TaskList` — Verify task structure
