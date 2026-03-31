# Python

## Project Structure

```
.
├── src/              # Source code (or named package)
├── tests/            # Test files (mirrors src)
├── pyproject.toml    # Project config
├── uv.lock           # Dependency lock
├── scripts/          # Utility scripts
└── configs/          # Config files
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `user_service.py` |
| Classes | PascalCase | `class UserService` |
| Functions | snake_case | `def get_user_by_id()` |
| Variables | snake_case | `max_retries` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Test files | `test_*.py` | `test_user_service.py` |

## Code Style

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: str
    name: str
    email: str

def get_user_by_id(user_id: str) -> Optional[User]:
    if not user_id:
        raise ValueError("user_id is required")
    return db.find_by_id(user_id)
```

**Follow:** Type hints, dataclasses for DTOs, descriptive names, explicit error handling

## Commands

```bash
uv sync                        # Install deps
uv run pytest                 # Run tests
uv run pytest --cov=.         # With coverage
ruff check .                  # Lint
ruff format .                 # Format
mypy .                        # Type check
```

## Patterns

- Use `uv` for package management
- Type hints on all public functions
- Use `dataclasses` or `pydantic` for data models
- Avoid `SELECT *` - always specify columns
