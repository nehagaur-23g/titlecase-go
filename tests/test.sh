#!/bin/bash
set -euo pipefail

mkdir -p /logs/verifier

# A failing pytest must not abort the script before reward.json is checked.
# Do not write reward.txt; reward.json is the weighted score from pytest.
if pytest -s --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA; then
  :
fi

if [ ! -s /logs/verifier/reward.json ]; then
  printf '%s\n' '{"reward": 0}' > /logs/verifier/reward.json
fi
