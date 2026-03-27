---
name: storage
description: Storage analysis skills to find total storage, available storage, and identify folders consuming large disk space.
---

# Storage Analysis Skill

This skill provides comprehensive storage analysis capabilities for macOS and Linux systems.

## Capabilities

1. **Total & Free Storage**: Check overall disk capacity and available space
2. **Large Folder Detection**: Identify folders consuming the most disk space
3. **Storage Reports**: Generate detailed storage usage reports

## Usage Instructions

### 1. Check Total and Free Storage

For **macOS**, use `df -h` for human-readable output:

```bash
df -h /
```

For more detailed macOS-specific information:

```bash
diskutil info / | grep -E "(Volume Name|Disk Size|Volume Free Space)"
```

For **Linux**, use `df -h`:

```bash
df -h /
```

Expected output includes:
- **Total Size**: Overall disk capacity
- **Used Space**: Amount currently consumed
- **Available Space**: Free space remaining
- **Use %**: Percentage of disk used

### 2. Find Large Folders

To identify the top 20 largest directories in the home directory:

```bash
du -h ~ 2>/dev/null | sort -hr | head -20
```

To analyze a specific directory (e.g., current directory):

```bash
du -h -d 1 . 2>/dev/null | sort -hr
```

To find large folders system-wide (requires patience):

```bash
sudo du -h / -d 2 2>/dev/null | sort -hr | head -30
```

**Parameters explained:**
- `du -h`: Disk usage in human-readable format (KB, MB, GB)
- `-d 1` or `-d 2`: Maximum depth to traverse (1 = immediate subdirectories)
- `sort -hr`: Sort by human-readable numbers in reverse (largest first)
- `head -20`: Show top 20 results
- `2>/dev/null`: Suppress permission errors

### 3. Analyze Specific Locations

Common locations to check for large files:

```bash
# Home directory breakdown
du -h -d 1 ~ | sort -hr

# Downloads folder
du -sh ~/Downloads/*

# Application support (macOS)
du -sh ~/Library/* 2>/dev/null | sort -hr | head -20

# Cache directories (macOS)
du -sh ~/Library/Caches/* 2>/dev/null | sort -hr | head -10

# Node modules (if you're a developer)
find ~ -name "node_modules" -type d -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -10
```

### 4. Quick Storage Summary

Create a comprehensive storage report:

```bash
echo "=== STORAGE SUMMARY ==="
echo ""
echo "Total & Free Space:"
df -h / | grep -v Filesystem
echo ""
echo "Top 10 Largest Directories in Home:"
du -h -d 1 ~ 2>/dev/null | sort -hr | head -10
echo ""
echo "Large Files (over 100MB) in Home:"
find ~ -type f -size +100M -exec du -h {} \; 2>/dev/null | sort -hr | head -10
```

## Advanced Usage

### Find Files by Size

Find all files larger than 1GB:

```bash
find ~ -type f -size +1G -exec du -h {} \; 2>/dev/null | sort -hr
```

Find all files larger than 500MB in current directory:

```bash
find . -type f -size +500M -exec du -h {} \; 2>/dev/null | sort -hr
```

### Clean Up Recommendations

After identifying large folders, common cleanup targets:
- `~/Downloads/`: Old downloads
- `~/Library/Caches/`: Application caches (macOS)
- `~/.npm/`: npm cache
- `~/.cache/`: Various app caches (Linux)
- `node_modules/`: Project dependencies (can be reinstalled)
- Old virtual environments, Docker images, build artifacts

## Platform-Specific Notes

### macOS
- Use `diskutil list` to see all drives
- Use `diskutil info /` for detailed volume information
- Time Machine backups can consume significant space
- Check `~/Library/Application Support/` for large app data

### Linux
- Use `lsblk` to list block devices
- Use `ncdu` (if installed) for interactive disk usage analysis
- Check `/var/log/` for large log files
- Docker images/containers can consume significant space

## Safety Tips

1. **Don't delete system files**: Only remove files from your home directory or known safe locations
2. **Use `-d 1` or `-d 2`**: Limit depth to avoid overwhelming output
3. **Check before deleting**: Always verify what a folder contains before removal
4. **Backup important data**: Before major cleanup operations

## Tool Integration

When implementing this skill in an agent, use the `exec_command` tool to execute these commands and parse the output for the user.

