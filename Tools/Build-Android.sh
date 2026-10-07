#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
unity_editor="${1:?Usage: Tools/Build-Android.sh /path/to/Unity-6000.6.3f1/Editor/Unity}"
if [[ ! -x "$unity_editor" ]]; then
  echo "Unity executable is missing or not executable: $unity_editor" >&2
  exit 2
fi
mkdir -p "$project_root/Logs"
exec "$unity_editor" -batchmode -quit -buildTarget Android -projectPath "$project_root" \
  -executeMethod Emberfall.Editor.AndroidBuild.BuildApk -logFile "$project_root/Logs/AndroidBuild.log"
