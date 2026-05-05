#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

export PYTHONPATH="$repo_root${PYTHONPATH:+:$PYTHONPATH}"
exec python -m agent_flight_recorder "$@"

