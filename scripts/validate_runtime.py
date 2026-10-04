"""Run Minecraft mod initialization and collision-cache checks before EULA/world load."""
import argparse
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--exhausted', action='store_true')
args = p.parse_args()
cmd = ['bash', './gradlew', '--no-daemon', 'runServer', '-I', str(root / 'scripts/validate_runtime.gradle')]
if args.exhausted:
    cmd.append('-PbtrExhausted=true')
result = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
print(result.stdout)
# Minecraft initialization failures can still make Gradle report BUILD SUCCESSFUL.
if result.returncode or '[main/ERROR]' in result.stdout or 'Validated 80 Polymer block states including collision caches.' not in result.stdout or 'Resource pack validation passed.' not in result.stdout:
    sys.exit('Minecraft block/resource validation failed; see output above')
if args.exhausted and 'No Polymer model states available' not in result.stdout:
    sys.exit('Pool exhaustion was not exercised')
print('Runtime validation passed (before EULA/world load).')
