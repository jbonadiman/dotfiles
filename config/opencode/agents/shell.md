# Shell

## Project Structure

```
.
├── scripts/          # Executable scripts
├── lib/              # Shared libraries (sourced)
├── tests/            # bats test files (*.bats)
└── .shellcheckrc     # Optional config
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Scripts | kebab-case | `deploy-app.sh` |
| Functions | snake_case | `deploy_app()` |
| Variables | UPPER_SNAKE_CASE | `APP_NAME` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Test files | `*.bats` | `deploy.bats` |

## Code Style

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly APP_NAME="myapp"
readonly MAX_RETRIES=3

deploy_app() {
    local version="${1:-latest}"
    local retries=0

    while (( retries < MAX_RETRIES )); do
        if curl -f "https://api.example.com/deploy/${version}"; then
            echo "Deployed successfully"
            return 0
        fi
        ((retries++))
        sleep "$((retries * 2))"
    done
    return 1
}
```

**Follow:** `set -euo pipefail`, `readonly` for constants, local vars, error returns

## Commands

```bash
shellcheck script.sh           # Lint
shfmt -w script.sh             # Format
bats test.bats                 # Run tests
bash -n script.sh              # Syntax check
```

## Patterns

- **Never** use `eval`
- **Never** use `#!/bin/bash` - use `#!/usr/bin/env bash`
- Always `set -euo pipefail`
- Use `local` for function variables
- Use `readonly` for constants
- Return exit codes explicitly
