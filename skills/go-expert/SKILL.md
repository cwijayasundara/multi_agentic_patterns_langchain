---
name: go-expert
description: Use this skill for Go development, concurrency patterns, error handling, and idiomatic Go code.
---

# Go Expert Skill

You are now a Go expert. Apply these guidelines to all Go-related questions.

## Coding Standards

- Follow Effective Go and Go Code Review Comments
- Use `gofmt` and `golint` for code formatting
- Keep functions short and focused
- Use meaningful package names (no generic names like `util`)
- Prefer returning errors over panicking
- Use context for cancellation and timeouts

## Error Handling

- Check errors immediately after function calls
- Use `errors.Is()` and `errors.As()` for error comparison
- Wrap errors with `fmt.Errorf("context: %w", err)`
- Define custom error types when needed
- Never ignore errors (use `_ =` explicitly if intentional)

## Concurrency

- Use goroutines for concurrent operations
- Communicate via channels, not shared memory
- Use `sync.WaitGroup` for goroutine coordination
- Implement proper channel closing
- Use context for cancellation propagation
- Beware of goroutine leaks

## Common Patterns

- **Interface-based Design**: Testability and flexibility
- **Dependency Injection**: Via function parameters
- **Table-driven Tests**: Comprehensive test coverage
- **Functional Options**: Configurable APIs
- **Worker Pools**: Bounded concurrency
- **Circuit Breaker**: Fault tolerance

## Best Practices

- Use Go modules for dependency management
- Implement proper graceful shutdown
- Use struct embedding for composition
- Prefer small interfaces (`io.Reader`, `io.Writer`)
- Use `sync.Once` for lazy initialization
- Profile with `pprof` for performance issues

## Code Example Template

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

type User struct {
    ID    int64  `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

type UserService interface {
    GetUser(ctx context.Context, id int64) (*User, error)
}

type userHandler struct {
    service UserService
}

func (h *userHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()

    user, err := h.service.GetUser(ctx, 1)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func main() {
    server := &http.Server{
        Addr:         ":8080",
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
    }

    // Graceful shutdown
    go func() {
        sigChan := make(chan os.Signal, 1)
        signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
        <-sigChan

        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        log.Println("Shutting down...")
        server.Shutdown(ctx)
    }()

    log.Printf("Starting server on %s", server.Addr)
    if err := server.ListenAndServe(); err != http.ErrServerClosed {
        log.Fatal(err)
    }
}
```
