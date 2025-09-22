# Quick Setup Commands for Future Sessions

## Session Startup (30 seconds instead of 2 hours!)

```bash
# 1. Check current state
python scripts/resume_work.py

# 2. Quick reference check
cat PATTERNS.md | head -20

# 3. See last session notes  
cat SESSION_NOTES.md | head -15
```

## Add these aliases to your shell profile:

```bash
# Add to ~/.bashrc or PowerShell profile
alias dwh-status="python scripts/resume_work.py"
alias dwh-patterns="cat PATTERNS.md"
alias dwh-commands="cat COMMANDS.md" 
alias dwh-notes="cat SESSION_NOTES.md"
```

## For PowerShell (add to $PROFILE):

```powershell
function dwh-status { python scripts/resume_work.py }
function dwh-patterns { Get-Content PATTERNS.md }
function dwh-commands { Get-Content COMMANDS.md }
function dwh-notes { Get-Content SESSION_NOTES.md }
```

## Next Session Workflow:

1. **Start**: `dwh-status` (shows everything you need to know)
2. **Check**: `dwh-patterns` (see what exists, don't recreate)
3. **Reference**: `dwh-commands` (copy/paste working code)
4. **Work**: Continue from established patterns
5. **End**: Update SESSION_NOTES.md with progress

**Result**: 30 seconds to full context instead of 2 hours of rediscovery!