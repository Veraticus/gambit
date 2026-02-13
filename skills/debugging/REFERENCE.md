# Debugging Examples and Patterns

Detailed examples for the debugging skill. See [SKILL.md](SKILL.md) for the process.

## Bad: Symptom Fix Without Investigation

```
Developer sees: NullPointerException at UserService:45

"Obviously email is null. Add null check."

String email = user.getEmail() != null ? user.getEmail().toLowerCase() : "";

Bug "fixed"... but crashes continue with different data.
```

**Why it fails:**
- Fixed symptom (null at line 45), not root cause
- Didn't investigate WHY email is null
- Root cause: Registration endpoint doesn't validate email
- Null-check applied everywhere, root cause unfixed

## Good: Systematic Investigation

```
Developer sees: NullPointerException at UserService:45

Phase 1: Create Task
  "Bug: NullPointerException in UserService.getEmail()"

Phase 2: Reproduce
  $ curl -X POST /api/register -d '{"name":"test"}'
  # Consistently returns 500

Phase 3: Investigate
  WebSearch: "NullPointerException getEmail java"
  Explore agent (subagent_type: "Explore"):
    "Find where User objects are created without email validation"

  Trace backward:
    UserService:45 ← email null
    Controller:23 ← User from RegistrationHandler
    RegistrationHandler:15 ← User created without email validation

  ROOT CAUSE: Registration doesn't validate email field

Phase 4: Write failing test
  @Test void registrationRequiresEmail() {
      assertThrows(ValidationException.class, () ->
          register(new UserDTO(null, "password")));
  }
  // RUN: FAILS (bug exists) ✓

Phase 5: Fix root cause
  @PostMapping("/register")
  public User register(@RequestBody UserDTO dto) {
      if (dto.getEmail() == null || dto.getEmail().isEmpty()) {
          throw new ValidationException("Email required");
      }
      return userService.create(dto);
  }
  // RUN: Test PASSES ✓
  // Full suite (via general-purpose agent): All pass ✓

Phase 6: Close Task
  Fix Status: FIXED
  Root cause: Registration endpoint missing email validation
  Fix: Added validation in RegistrationHandler:15
  Regression test: registrationRequiresEmail
```

## Bad: Test Written After Fix

```
Developer fixes validation bug, then writes test:

def validate_email(email):
    return "@" in email and len(email) > 0  # Fix

def test_validate_email():
    assert validate_email("user@example.com") == True  # Test after

# Test passes immediately - but only tests happy path
# Later, someone breaks validation:
def validate_email(email):
    return True  # Oops!

# Test STILL PASSES (only checked happy path)
```

**Why it fails:**
- Test written after fix — never saw it fail
- Only tests happy path remembered
- Doesn't test the actual bug (empty email)
- Regression goes undetected

## Good: Test Written Before Fix (RED-GREEN)

```
Phase 4: Write failing test FIRST
def test_empty_email_rejected():
    assert validate_email("") == False  # The bug case

def test_no_at_symbol_rejected():
    assert validate_email("invalid") == False

# RUN: FAILS (bug exists) ✓

Phase 5: Implement fix
def validate_email(email):
    if not email or "@" not in email:
        return False
    return True

# RUN: PASSES ✓

# Later regression attempt:
def validate_email(email):
    return True  # Oops!

# TEST CATCHES IT:
# FAIL: assert validate_email("") == False
```

## Investigation Patterns

### Single-Component Bug

Use Read and Grep to trace through the code directly:

```
1. Read the error location
2. Grep for callers of the failing function
3. Read each caller, trace the data
4. Identify where bad value enters
```

### Multi-Component Bug

Dispatch an Explore agent to map the system:

```
Task
  subagent_type: "Explore"
  description: "Map data flow for [feature]"
  prompt: |
    Trace the request flow for [operation]:
    1. Where does the request enter? (handler/controller)
    2. What services process it?
    3. What database queries run?
    4. Where could data be lost or corrupted?
```

Add diagnostic logging at boundaries, run once, analyze:

```python
# Handler
logger.debug(f"=== Handler received: {request.json}")

# Service
logger.debug(f"=== Service processing: {order}")

# Repository
logger.debug(f"=== Query result: {result}")
```

### Intermittent Bug

1. Add instrumentation, don't try to fix
2. Run multiple times, collect data
3. Look for patterns (timing, concurrency, input variation)
4. If timing-related: check for race conditions or arbitrary timeouts

### Performance Bug

1. Profile before optimizing — measure, don't guess
2. Identify the bottleneck with actual numbers
3. Fix the bottleneck, re-measure
4. If no clear bottleneck: check for N+1 queries, missing indices, unnecessary work
