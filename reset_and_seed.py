import subprocess
import sys

scripts = [
    "reset_database.py",
    "setup_database.py",
    "seed_data.py",
]

for script in scripts:
    print(f"\n{'='*40}")
    print(f"Running: {script}")
    print('='*40)
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"FAILED: {script} — stopping.")
        break
    print(f"Done: {script}")

print("\nAll done — ready to test!")
