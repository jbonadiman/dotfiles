# Go

## Project Structure

```
.
├── cmd/              # Applications (main packages)
├── internal/         # Private code (pkg, app subdirs)
├── pkg/              # Public libraries
├── api/              # API definitions (proto, OpenAPI)
├── configs/          # Config files
├── scripts/          # Build scripts
├── test/             # Integration tests
└── go.mod
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Packages | lowercase, no underscore | `package userpkg` |
| Exported | PascalCase | `GetUserByID()` |
| Unexported | camelCase | `getUserByID()` |
| Interfaces | -er suffix | `Reader`, `Writer` |
| Errors | `Err` prefix | `ErrNotFound` |
| Test files | `*_test.go` | `user_test.go` |

## Code Style

```go
func (s *UserService) GetUserByID(ctx context.Context, id string) (*User, error) {
    if id == "" {
        return nil, ErrInvalidID
    }
    user, err := s.repo.FindByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("fetching user: %w", err)
    }
    return user, nil
}
```

**Follow:** context usage, error wrapping, early returns, small functions

## Commands

```bash
go mod tidy && go vet ./...   # Verify deps
go test -v ./...             # Test all
go test -coverprofile=c.out  # With coverage
golangci-lint run            # Lint
gofmt -w .                   # Format
```

## Patterns

- Use `context.Context` for cancellation/timeouts
- Return errors with `fmt.Errorf("doing X: %w", err)`
- Keep packages small; avoid `internal/` sprawl
