# setup_git.py
import subprocess
import sys

commands = [
    ["git", "init"],
    ["git", "add", "."],
    ["git", "commit", "-m", "initial commit — autonomous job hunter"],
]

for cmd in commands:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"OK: {' '.join(cmd)}")
    else:
        print(f"ERROR: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)

print("\nDone. Now go to github.com, create a new repo,")
print("then run the two commands it shows you to push.")
