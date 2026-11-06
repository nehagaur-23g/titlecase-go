#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "${script_dir}/main.go" ./main.go
cp "${script_dir}/go.mod" ./go.mod

gofmt -w main.go
go build -o /tmp/titlecase-go .

find . -type f -name '*.py' -delete

mkdir -p /logs/artifacts/repo
cp main.go go.mod /logs/artifacts/repo/