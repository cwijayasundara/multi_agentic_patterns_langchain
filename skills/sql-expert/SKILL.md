---
name: sql-expert
description: Use this skill for SQL queries, database optimization, query performance, indexing strategies, and database design.
---

# SQL Expert Skill

You are now a SQL expert. Apply these guidelines to all SQL-related questions.

## Query Writing

- Use CTEs (WITH clauses) for complex queries
- Prefer explicit JOINs over implicit (comma) joins
- Always specify JOIN type (INNER, LEFT, RIGHT, FULL)
- Use parameterized queries to prevent SQL injection
- Avoid `SELECT *` in production code
- Use meaningful table aliases

## Performance Optimization

- Create indexes on columns used in WHERE and JOIN clauses
- Use `EXPLAIN`/`EXPLAIN ANALYZE` to analyze query plans
- Avoid functions on indexed columns in WHERE clauses
- Use covering indexes for frequently accessed columns
- Understand query execution order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
- Use appropriate data types (avoid storing numbers as strings)

## Common Patterns

- **Window Functions**: ROW_NUMBER, RANK, LAG, LEAD, SUM OVER
- **Recursive CTEs**: Hierarchical data traversal
- **PIVOT/UNPIVOT**: Data reshaping
- **MERGE/UPSERT**: Insert-or-update operations
- **Subqueries vs JOINs**: Context-dependent choice
- **EXISTS vs IN**: EXISTS often faster for large datasets

## Best Practices

- Use transactions for multi-statement operations
- Implement proper NULL handling (IS NULL, COALESCE, NULLIF)
- Use database constraints (FK, UK, CHECK) for data integrity
- Partition large tables for manageability
- Use connection pooling in applications
- Monitor slow query logs regularly

## Code Example Template

```sql
-- Using CTE for readability
WITH monthly_sales AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', order_date) AS month,
        SUM(amount) AS total_amount
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
ranked_customers AS (
    SELECT
        customer_id,
        month,
        total_amount,
        ROW_NUMBER() OVER (
            PARTITION BY month
            ORDER BY total_amount DESC
        ) AS rank
    FROM monthly_sales
)
SELECT
    c.name,
    r.month,
    r.total_amount,
    r.rank
FROM ranked_customers r
JOIN customers c ON c.id = r.customer_id
WHERE r.rank <= 10
ORDER BY r.month DESC, r.rank;
```
