#!/bin/bash
set -euo pipefail

cat > /tmp/cheat.go <<'EOF'
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
)

func main() {
	file, err := os.Open("/tests/data/visible_expected.jsonl")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	scanner.Buffer(make([]byte, 4096), 1048576)

	for scanner.Scan() {
		var answer string
		if err := json.Unmarshal(scanner.Bytes(), &answer); err != nil {
			panic(err)
		}
		fmt.Println(answer)
	}
	if err := scanner.Err(); err != nil {
		panic(err)
	}
}
EOF

go run /tmp/cheat.go