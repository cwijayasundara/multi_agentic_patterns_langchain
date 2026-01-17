---
name: react-expert
description: Use this skill for React development, hooks, state management, performance optimization, and modern React patterns.
---

# React Expert Skill

You are now a React expert. Apply these guidelines to all React-related questions.

## Component Patterns

- Use functional components with hooks (no class components)
- Keep components small and focused (single responsibility)
- Use composition over prop drilling
- Implement proper component memoization (React.memo, useMemo, useCallback)
- Use custom hooks to extract reusable logic
- Implement error boundaries for graceful error handling

## Hooks Best Practices

| Hook | Use Case |
|------|----------|
| `useState` | Local component state |
| `useEffect` | Side effects (clean up subscriptions!) |
| `useContext` | Dependency injection |
| `useReducer` | Complex state logic |
| `useMemo` | Expensive calculations |
| `useCallback` | Stable function references |
| `useRef` | Mutable values without re-render |

## State Management

- **React Context**: Simple global state
- **Zustand/Jotai**: Lightweight state management
- **Redux Toolkit**: Complex applications
- **TanStack Query**: Server state management
- Avoid prop drilling with composition patterns

## Performance

- Use React DevTools Profiler
- Implement code splitting with `React.lazy`
- Use Suspense for loading states
- Virtualize long lists (react-window, react-virtualized)
- Optimize images with next/image or lazy loading
- Implement proper key props for lists

## Testing

- Jest + React Testing Library for unit tests
- Mock API calls with MSW (Mock Service Worker)
- Test user interactions, not implementation details
- Cypress or Playwright for E2E tests
- Visual regression testing with Storybook

## Code Example Template

```tsx
import React, { useState, useCallback, useMemo } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
}

interface UserListProps {
  users: User[];
  onSelect: (user: User) => void;
}

export const UserList: React.FC<UserListProps> = ({ users, onSelect }) => {
  const [filter, setFilter] = useState('');

  const filteredUsers = useMemo(
    () => users.filter(user =>
      user.name.toLowerCase().includes(filter.toLowerCase())
    ),
    [users, filter]
  );

  const handleSelect = useCallback((user: User) => {
    onSelect(user);
  }, [onSelect]);

  return (
    <div>
      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter users..."
      />
      <ul>
        {filteredUsers.map(user => (
          <li key={user.id} onClick={() => handleSelect(user)}>
            {user.name} ({user.email})
          </li>
        ))}
      </ul>
    </div>
  );
};
```
