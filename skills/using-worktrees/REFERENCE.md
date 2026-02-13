# Using Worktrees: Reference Examples

## Good: Complete Workflow with Devenv

```
Claude: "I'm using gambit:using-worktrees to set up an isolated workspace."

Step 1: Check existing directories
$ ls -d .worktrees 2>/dev/null
.worktrees

Step 4: Verify gitignored (skipped 2-3, directory exists)
$ git check-ignore -q .worktrees && echo "ignored"
ignored

Step 5: Create worktree
$ git worktree add .worktrees/auth -b feature/auth
Preparing worktree (new branch 'feature/auth')
HEAD is now at abc123 Previous commit

Step 6: Environment setup
$ [ -f devenv.nix ] && echo "devenv"
devenv
$ grep -l "DATABASE_URL" devenv.nix
devenv.nix

[AskUserQuestion about database strategy]
User selects: Share database

$ cd .worktrees/auth && direnv allow
direnv: loading .envrc

Step 7: Verify baseline
$ go test ./...
ok  	myproject/...	0.847s
47 tests passed

Step 8: Report
Worktree ready at /home/dev/myproject/.worktrees/auth
Branch: feature/auth
Tests: 47 passing, 0 failures
Environment: devenv (shared database)

Ready to implement OAuth authentication
```

**Why it works:**
- Followed directory priority (existing dir found)
- Verified gitignore before creating anything
- Asked about database strategy (didn't assume)
- Ran baseline tests to establish known-good state
- Reported full absolute path

---

## Good: Node.js Project, No Existing Directory

```
Claude: "I'm using gambit:using-worktrees to set up an isolated workspace."

Step 1: Check existing directories
$ ls -d .worktrees 2>/dev/null
(nothing)
$ ls -d worktrees 2>/dev/null
(nothing)

Step 2: Check CLAUDE.md
$ grep -i "worktree" CLAUDE.md 2>/dev/null
(no match)

Step 3: Ask user
[AskUserQuestion: "No worktree directory found. Where should I create worktrees?"]
User selects: .worktrees/ (Recommended)

Step 4: Verify gitignored
$ git check-ignore -q .worktrees 2>/dev/null
(exit code 1 — not ignored)

$ echo ".worktrees/" >> .gitignore
$ git add .gitignore && git commit -m "chore: add worktree directory to gitignore"
[main abc123] chore: add worktree directory to gitignore

Step 5: Create worktree
$ git worktree add .worktrees/dashboard -b feature/dashboard
Preparing worktree (new branch 'feature/dashboard')

Step 6: Environment setup (Node.js)
$ cd .worktrees/dashboard
$ [ -f package.json ] && echo "node"
node
$ ls yarn.lock pnpm-lock.yaml 2>/dev/null
(nothing — use npm)
$ npm install
added 847 packages in 12s

Step 7: Verify baseline
$ npm test
Tests: 92 passed, 0 failed

Step 8: Report
Worktree ready at /home/dev/webapp/.worktrees/dashboard
Branch: feature/dashboard
Tests: 92 passing, 0 failures
Environment: npm

Ready to implement dashboard redesign
```

---

## Bad: Skip Gitignore Verification

```
[Check .worktrees/ — doesn't exist]
[Create .worktrees/feature directly without checking ignore]  # WRONG

# Later...
$ git status
Untracked files:
  .worktrees/feature/node_modules/
  .worktrees/feature/src/
  ... (hundreds of files)
```

**Why it fails:**
- Worktree contents pollute git status
- Risk of accidentally committing worktree
- Hard to undo without losing work

---

## Bad: Proceed with Failing Tests Silently

```
[Create worktree]
[Run tests — 3 failures]
[Continue without asking]  # WRONG

# Later...
[Implement feature]
[Run tests — 5 failures]
# Which 2 failures are new? Can't tell.
```

**Why it fails:**
- Can't distinguish new bugs from pre-existing
- Wastes time debugging inherited failures
- Uncertain baseline undermines confidence

---

## Bad: Assume Directory Location

```
User: "Create a worktree for the auth feature"

$ git worktree add .worktrees/auth -b feature/auth  # WRONG — skipped Steps 1-3

# User wanted worktrees in ~/dev/worktrees/ (set in CLAUDE.md)
# Now there's a .worktrees/ directory they didn't want
```

**Why it fails:**
- Ignored user's configured preference
- Created directory in wrong location
- User has to clean up and redo

---

## Bad: Skip Database Strategy Question

```
[Detect devenv with DATABASE_URL]
[Assume shared database]  # WRONG — didn't ask

$ direnv allow
# Worktree now shares production database
# User wanted isolated database for destructive migration testing
```

**Why it fails:**
- Database isolation is a critical choice with real consequences
- Shared vs isolated affects what operations are safe
- User might need clean-slate database for testing migrations
