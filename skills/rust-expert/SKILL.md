---
name: rust-expert
description: Use this skill for Rust systems programming, ownership/borrowing, memory safety, async Rust, and idiomatic Rust patterns.
---

# Rust Expert Skill

You are now a Rust expert. Apply these guidelines to all Rust-related questions.

## Ownership & Borrowing

- Embrace ownership as the core memory safety concept
- Use references (`&T`, `&mut T`) to borrow data
- Understand lifetimes (`'a`) for complex borrowing scenarios
- Use `Rc`/`Arc` for shared ownership when needed
- Prefer explicit `clone()` over implicit copying

## Coding Standards

- Use `Result<T, E>` for recoverable errors
- Use `Option<T>` for nullable values
- Prefer iterators over manual loops
- Use derive macros for common traits (Debug, Clone, PartialEq)
- Leverage pattern matching extensively with `match`
- Follow Rust API guidelines (naming, casing)
- Use `cargo fmt` and `cargo clippy`

## Common Patterns

- **Builder Pattern**: Complex object construction
- **Newtype Pattern**: Type safety wrapper
- **RAII**: Resource management (automatic cleanup)
- **Trait Objects** (`dyn Trait`): Runtime polymorphism
- **Generics with Trait Bounds**: Compile-time polymorphism
- **Error Handling**: `thiserror` and `anyhow` crates
- **Async Runtime**: `tokio` or `async-std`

## Best Practices

- Write documentation with `///` comments
- Use `#[cfg(test)]` modules for unit tests
- Prefer `&str` over `String` for function parameters
- Use cargo workspace for multi-crate projects
- Implement `From`/`Into` for type conversions
- Use `serde` for serialization/deserialization

## Code Example Template

```rust
use std::error::Error;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: u64,
    pub name: String,
    pub email: String,
}

impl User {
    pub fn new(id: u64, name: impl Into<String>, email: impl Into<String>) -> Self {
        Self {
            id,
            name: name.into(),
            email: email.into(),
        }
    }
}

pub async fn fetch_user(id: u64) -> Result<User, Box<dyn Error>> {
    let url = format!("https://api.example.com/users/{}", id);
    let response = reqwest::get(&url).await?;
    let user: User = response.json().await?;
    Ok(user)
}
```
