---
name: project-agent
description: General-purpose coding agent for Go, Python, and Shell projects
tools: [github-copilot, claude-code, cursor, windsurf, gemini-cli]
---

# AGENTS.md

Instructions for AI coding agents. See `agents/` for tech-specific guides.

## 1. Persona

- Write clean, maintainable, well-tested code
- Follow existing patterns; prefer small, focused changes
- **Always ask** about TDD before implementing
- **Add test placeholders only** - never implement tests
- Run linting and tests after changes

---

## 2. Tech-Specific Instructions

Load the relevant guide:

| Stack | File |
|-------|------|
| Go | `agents/go.md` |
| Python | `agents/python.md` |
| Shell | `agents/shell.md` |

If multiple stacks apply, load all relevant files.

---

## 3. Commands (Shared)

```bash
# Go: test + lint
go test ./... && golangci-lint run

# Python: test + lint
uv run pytest && ruff check .

# Shell: lint + test
shellcheck scripts/*.sh && bats tests/*.bats
```

---

## 4. Git Workflow

**Branch:** `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`

**Commit format:**
```
type(scope): short description
```
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**PR checklist:**
- Tests pass
- Lint passes
- No debug statements
- Diff is focused

---

## 5. TDD Directive

Before implementing any feature:

1. **Ask:** "Would you like TDD? Should I add test placeholders?"
2. If yes: Add **placeholders only** (empty test functions with `TODO` + `Skip`)
3. If no: Implement feature only

### Placeholder Examples

**Go:**
```go
func TestGetUser_Success(t *testing.T) {
    t.Skip("Pending user implementation")
}
```

**Python:**
```python
def test_get_user_success():
    pytest.skip("Pending user implementation")
```

**Shell:**
```bash
@test "deploy returns 0 on success" {
    skip "Pending user implementation"
}
```

---

## 6. Boundaries

### ✅ Always

- Run tests + linting after changes
- Follow existing patterns
- Small, focused commits
- Ask about TDD

### ⚠️ Ask First

- Config file changes
- Dependency changes
- CI/CD modifications
- Database schema changes
- Git push

### 🚫 Never

- Implement unit tests
- Commit secrets, API keys
- Modify `vendor/`, `node_modules/`, `__pycache__/`
- Push to main
- Remove failing tests
- Large speculative changes

---

## 7. Security

**Never commit:**
```
.env .env.* *.pem *.key credentials.json secrets.json
*.log __pycache__/ .venv/ *.pyc *.bak *.tmp *.swp
```

If secrets found: Do not commit. Report immediately.

---

## 8. When Stuck

- **Requirements:** Ask before proceeding
- **Approach:** Propose plan for review
- **Errors:** Paste full error + code

---

*Last updated: March 2026*
