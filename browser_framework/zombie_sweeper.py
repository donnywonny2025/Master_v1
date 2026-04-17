#!/usr/bin/env python3
"""
Framework Zombie Sweeper
Hunts down and slaughters ghost processes associated with the Universal Browser Framework.
Ensures ports (like 9222) and RAM are cleanly freed.
"""

import os
import signal
import subprocess

def find_and_kill(pattern, exempt_pid=None):
    try:
        # Ask the OS for any process matching our pattern
        cmd = f"pgrep -f '{pattern}'"
        result = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
        
        killed_count = 0
        for pid_str in result:
            if not pid_str:
                continue
            pid = int(pid_str)
            # Do not kill ourselves, and do NOT kill the explicitly authorized exempt_pid
            if pid != os.getpid() and pid != exempt_pid:
                try:
                    os.kill(pid, signal.SIGKILL)
                    print(f"Slaughtered Zombie: {pattern} (PID {pid})")
                    killed_count += 1
                except ProcessLookupError:
                    pass
        return killed_count
    except subprocess.CalledProcessError:
        # pgrep returns 1 if nothing is found, which is totally fine
        return 0

def get_active_pid():
    lock_file = os.path.join(os.getcwd(), ".tmp", "amos_browser.pid")
    if os.path.exists(lock_file):
        with open(lock_file) as f:
            pid_str = f.read().strip()
            if pid_str.isdigit():
                return int(pid_str)
    return None

def clean_locks():
    # Attempt to remove the soft lock file if the process died violently
    lock_file = os.path.join(os.getcwd(), ".tmp", "amos_browser.pid")
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print("Cleared stale PID lock file.")

def run_sweep():
    print("Initiating Zombie Sweep...")
    active_pid = get_active_pid()
    if active_pid:
        print(f"Protecting Active AMOS Browser (PID {active_pid})")
    
    # 1. Kill any stray AMOS browser python wrappers
    python_count = find_and_kill('amos_browser.py', exempt_pid=active_pid)
    
    # 2. Kill stray chromium instances locking the CDP port
    # Note: chromium child processes have different PIDs, but this ensures we don't blindly crash our parent python
    chrome_count = find_and_kill('remote-debugging-port=9222', exempt_pid=active_pid)
    
    clean_locks()
    
    total = python_count + chrome_count
    if total == 0:
        print("Clear. No zombies detected.")
    else:
        print(f"Sweep complete. Executed {total} ghost processes freeing ports and RAM.")

if __name__ == "__main__":
    run_sweep()
