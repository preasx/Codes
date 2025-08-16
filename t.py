import asyncio
import random
import subprocess
from datetime import datetime, timedelta

SCRIPTS = ["test1.py", "test2.py", "test3.py", "test4.py"]
RUNS_PER_DAY = 20
MIN_DELAY = 4 * 60  # 15 min
MAX_DELAY = 15 * 60  # 45 min

last_script = None
run_counts = {script: 0 for script in SCRIPTS}
day_start = datetime.now()

def is_any_script_running():
    """Check if any of our scripts is already running."""
    result = subprocess.run(
        ["tasklist"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    output = result.stdout.lower()
    for script in SCRIPTS:
        if script.lower() in output:
            return True
    return False

def kill_old_scripts():
    """Force kill any of our scripts still running."""
    for script in SCRIPTS:
        subprocess.run(
            f"taskkill /F /FI \"WINDOWTITLE eq Run {script}\"",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def run_in_new_window(script_name):
    """Open the script in a new Command Prompt window that closes after finish."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching {script_name} in a new window...")
    subprocess.Popen(
        f'start "Run {script_name}" cmd /c python "{script_name}"',
        shell=True
    )

async def scheduler():
    global last_script, run_counts, day_start

    while True:
        # Reset daily run counts every 24 hours
        if datetime.now() - day_start >= timedelta(days=1):
            run_counts = {script: 0 for script in SCRIPTS}
            day_start = datetime.now()
            print("[*] Daily counters reset.")

        available_scripts = [s for s in SCRIPTS if run_counts[s] < RUNS_PER_DAY and s != last_script]

        if not available_scripts:
            sleep_until_reset = (day_start + timedelta(days=1) - datetime.now()).total_seconds()
            print(f"✅ All scripts done for today. Sleeping {sleep_until_reset//3600:.0f}h {(sleep_until_reset%3600)//60:.0f}m until reset.")
            await asyncio.sleep(sleep_until_reset)
            continue

        # Wait until no script is running
        while is_any_script_running():
            print("[!] A script is still running. Waiting 1 minute before retry...")
            await asyncio.sleep(60)

        # Kill any leftover windows just in case
        kill_old_scripts()

        # Pick and run a new script
        script = random.choice(available_scripts)
        last_script = script
        run_counts[script] += 1
        run_in_new_window(script)

        # Delay before next run
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Next run in {delay//60}m {delay%60}s.\n")
        await asyncio.sleep(delay)

if __name__ == "__main__":
    try:
        asyncio.run(scheduler())
    except KeyboardInterrupt:
        print("Scheduler stopped manually.")