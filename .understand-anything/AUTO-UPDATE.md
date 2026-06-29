# Automatic Knowledge Graph Updates

## Setup Enabled ✅

The knowledge graph is now configured for **automatic incremental updates** on every commit.

### How It Works

1. **Post-Commit Hook** (`.git/hooks/post-commit`)
   - Runs automatically after each `git commit`
   - Detects changed files (via git diff)
   - Re-analyzes only changed files (fast)
   - Updates knowledge graph in the background
   - Never blocks your commits

2. **Incremental Updates**
   - Compares git commit hash stored in `meta.json`
   - Only scans new/modified files
   - Updates node/edge relationships
   - Preserves existing graph structure
   - ~30-60 seconds for typical changes

### Manual Commands

```bash
# Check graph status
make graph-status

# Force immediate update
make graph-update

# Watch mode (continuous scanning)
make graph-watch

# Clean up old trash directories
make graph-clean
```

### Logs

Update logs are saved to: `.understand-anything/.update.log`

```bash
# View recent updates
tail -20 .understand-anything/.update.log
```

### Configuration

**To disable automatic updates:**
```bash
chmod -x .git/hooks/post-commit
```

**To re-enable:**
```bash
chmod +x .git/hooks/post-commit
```

### What Triggers Updates

- ✅ Any commit (including merges)
- ✅ Modified Java files
- ✅ Modified YAML/JSON configs
- ✅ Modified tests
- ✅ Any file in `src/` directory

### Performance

- **First run**: ~8 minutes (full analysis)
- **Subsequent updates**: ~1-2 minutes (incremental)
- **Post-commit time**: <2 seconds (runs in background)

### Dashboard Auto-Refresh

The dashboard will show cached data. To refresh:
1. **Hard refresh browser**: `Cmd+Shift+R`
2. **Or restart dashboard**: `/understand-dashboard`

### Example Workflow

```bash
# Make code changes
vim src/main/java/com/aipoc/service/TimeService.java

# Commit (auto-update runs in background)
git commit -m "feat: add new feature"

# Push (auto-update still running)
git push origin main

# Later, view what changed
tail .understand-anything/.update.log
```

---

**Last enabled:** 2026-06-28
**Hook version:** 1.0
