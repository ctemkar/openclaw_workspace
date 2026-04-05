# Project Structure - Organized Workspace

## 📁 Folder Organization

### **Root Directory (Clean)**
- `AGENTS.md` - Agent configurations
- `HEARTBEAT.md` - System status and tasks
- `SOUL.md` - Personality and behavior
- `IDENTITY.md` - Assistant identity
- `USER.md` - User information
- `TOOLS.md` - Available tools
- `MEMORY.md` - Persistent memory

### **📂 logs/** - All log files
- Trading logs, error logs, system logs
- Organized by date/type
- Easy to find and analyze

### **📂 scripts/** - All executable scripts
- Python trading bots
- Shell scripts
- Monitoring scripts
- All in one place

### **📂 config/** - Configuration files
- JSON configs
- API configurations
- Service files (.plist, .service)
- PID files

### **📂 bots/** - Bot-specific files
- Bot configurations
- Bot state files
- Bot templates

### **📂 dashboards/** - Dashboard files
- HTML dashboards
- CSS/JS for interfaces
- Dashboard configurations

### **📂 docs/** - Documentation
- Guides, instructions, plans
- README files
- Setup documentation
- API documentation

### **📂 reports/** - Generated reports
- Profit summaries
- Trading reports
- Analysis reports
- Progress reports

### **📂 backups/** - Backup files
- Script backups
- Config backups
- Historical data

### **📂 static/** - Static web files
- HTML pages
- CSS/JavaScript
- Images/assets

### **📂 secure/** - Secure storage
- Encrypted files
- Secure configurations

### **📂 secure_keys/** - API keys (symlinked)
- Exchange API keys
- Service credentials
- **Note**: Actual keys are symlinked from secure location

## 🔄 How to Run Things Now

### **Run a trading bot:**
```bash
cd scripts
python3 make_money_now.py > ../logs/REAL_trading.log 2>&1 &
```

### **Check logs:**
```bash
tail -f logs/REAL_trading.log
```

### **Run progress monitor:**
```bash
cd scripts
./progress_monitor.sh
```

### **Update configurations:**
```bash
cd config
# Edit JSON configs
```

## 🎯 Benefits of This Structure

1. **Clean root folder** - Easy to navigate
2. **Logical organization** - Files grouped by purpose
3. **Easy maintenance** - Know where everything is
4. **Better backups** - Can backup specific folders
5. **Scalable** - Easy to add new categories
6. **Professional** - Looks organized and managed

## 📊 File Count by Category
- Logs: 300+ files (now organized in `/logs`)
- Scripts: 120+ files (now in `/scripts`)
- Configs: 100+ files (now in `/config`)
- Docs: 60+ files (now in `/docs`)
- Reports: 140+ files (now in `/reports`)

## 🚀 Quick Start After Reorganization

1. **All scripts are in `/scripts/`**
2. **All logs are in `/logs/`**
3. **All configs are in `/config/`**
4. **Run from root, reference paths correctly**

Example: `./scripts/progress_monitor.sh` or `python3 scripts/make_money_now.py`