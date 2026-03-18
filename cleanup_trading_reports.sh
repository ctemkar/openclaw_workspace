#!/bin/bash
# Cleanup old trading reports and organize files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Cleaning up trading reports ==="
echo "Current directory: $(pwd)"
echo ""

# Create directories for organization
mkdir -p reports/archive reports/daily reports/weekly logs/archive

# Keep only the last 7 days of reports
echo "Archiving reports older than 7 days..."
find . -name "trading_report_*.txt" -mtime +7 -exec mv {} reports/archive/ \; 2>/dev/null || true
find . -name "trading_data_processing_*.log" -mtime +7 -exec mv {} logs/archive/ \; 2>/dev/null || true

# Move today's reports to daily folder
echo "Organizing today's reports..."
find . -name "trading_report_*.txt" -mtime -1 -exec mv {} reports/daily/ \; 2>/dev/null || true
find . -name "trading_data_processing_*.log" -mtime -1 -exec mv {} logs/ \; 2>/dev/null || true

# Move weekly summaries
echo "Organizing weekly summaries..."
find . -name "*summary*.txt" -mtime -7 ! -name "trading_summary_latest.txt" -exec mv {} reports/weekly/ \; 2>/dev/null || true

# Clean up old files (keep only last 30 of each type)
echo "Cleaning up old files..."
cd reports/daily 2>/dev/null && ls -t trading_report_*.txt 2>/dev/null | tail -n +31 | xargs rm -f 2>/dev/null || true
cd "$SCRIPT_DIR"
cd logs 2>/dev/null && ls -t trading_data_processing_*.log 2>/dev/null | tail -n +31 | xargs rm -f 2>/dev/null || true
cd "$SCRIPT_DIR"

# Display current organization
echo ""
echo "=== Current Organization ==="
echo "Reports/daily: $(ls reports/daily/*.txt 2>/dev/null | wc -l) files"
echo "Reports/weekly: $(ls reports/weekly/*.txt 2>/dev/null | wc -l) files"
echo "Reports/archive: $(ls reports/archive/*.txt 2>/dev/null | wc -l) files"
echo "Logs: $(ls logs/*.log 2>/dev/null | wc -l) files"
echo "Logs/archive: $(ls logs/archive/*.log 2>/dev/null | wc -l) files"
echo ""
echo "Latest summary files in root:"
ls -la *summary*.txt 2>/dev/null | head -5
echo ""
echo "Cleanup complete!"