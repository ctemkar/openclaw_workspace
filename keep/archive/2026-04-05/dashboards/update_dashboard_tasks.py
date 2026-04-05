#!/usr/bin/env python3
"""
Update dashboard tasks from memory files.
This script reads memory files and extracts tasks to update the dashboard.
"""

import os
import json
import glob
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
TASKS_FILE = os.path.join(BASE_DIR, "dashboard_tasks.json")

def read_memory_files():
    """Read all memory files and extract tasks."""
    tasks = []
    
    # Get all memory files
    memory_files = glob.glob(os.path.join(MEMORY_DIR, "*.md"))
    
    for mem_file in sorted(memory_files):
        try:
            with open(mem_file, 'r') as f:
                content = f.read()
                
            # Extract date from filename (format: YYYY-MM-DD.md)
            filename = os.path.basename(mem_file)
            date_str = filename.replace('.md', '')
            
            # Parse content for tasks
            lines = content.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('###'):
                    current_section = line.replace('###', '').strip()
                elif line.startswith('*') or line.startswith('-'):
                    # This is a task/item
                    task_text = line.lstrip('*- ').strip()
                    if task_text:
                        tasks.append({
                            'date': date_str,
                            'section': current_section or 'General',
                            'task': task_text,
                            'source_file': filename
                        })
        except Exception as e:
            print(f"Error reading {mem_file}: {e}")
    
    return tasks

def update_dashboard_tasks(tasks):
    """Update the dashboard tasks file."""
    try:
        # Create tasks data structure
        tasks_data = {
            'last_updated': datetime.now().isoformat(),
            'total_tasks': len(tasks),
            'tasks': tasks
        }
        
        # Save to file
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks_data, f, indent=2)
        
        print(f"Updated dashboard with {len(tasks)} tasks from memory files.")
        print(f"Tasks saved to: {TASKS_FILE}")
        
        return True
    except Exception as e:
        print(f"Error updating dashboard tasks: {e}")
        return False

def main():
    """Main function to update dashboard tasks."""
    print(f"Reading memory files from: {MEMORY_DIR}")
    
    # Read tasks from memory files
    tasks = read_memory_files()
    
    if not tasks:
        print("No tasks found in memory files.")
        return
    
    # Update dashboard tasks
    success = update_dashboard_tasks(tasks)
    
    if success:
        print("Dashboard tasks updated successfully.")
    else:
        print("Failed to update dashboard tasks.")

if __name__ == "__main__":
    main()