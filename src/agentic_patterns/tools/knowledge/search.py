"""
Knowledge base search tools for the router pattern.

These tools search mock knowledge bases for documentation, FAQs, and tutorials.
In production, these would connect to actual search infrastructure.
"""

from langchain_core.tools import tool


# Mock Knowledge Bases
DOCS_KNOWLEDGE = {
    "api_authentication": """
API Authentication Guide:
- All API requests require an API key in the Authorization header
- Format: Authorization: Bearer <your-api-key>
- API keys can be generated in the dashboard under Settings > API Keys
- Keys can have read-only or read-write permissions
- Rate limits: 1000 requests/minute for standard tier, 10000 for enterprise
""",
    "api_endpoints": """
Core API Endpoints:
- GET /api/v1/users - List all users
- POST /api/v1/users - Create a new user
- GET /api/v1/users/{id} - Get user by ID
- PUT /api/v1/users/{id} - Update user
- DELETE /api/v1/users/{id} - Delete user
- All endpoints return JSON responses
- Pagination via ?page=N&limit=M parameters
""",
    "database_schema": """
Database Architecture:
- PostgreSQL 15 with read replicas
- Users table: id, email, name, created_at, updated_at
- Sessions table: id, user_id, token, expires_at
- Events table: id, user_id, type, payload, timestamp
- Indexes on all foreign keys and commonly queried fields
""",
}

FAQ_KNOWLEDGE = {
    "pricing": """
Pricing FAQ:
Q: What plans are available?
A: We offer Free, Pro ($29/mo), and Enterprise (custom) plans.

Q: Is there a free trial?
A: Yes, Pro plan includes a 14-day free trial. No credit card required.

Q: Can I change plans anytime?
A: Yes, upgrades are immediate. Downgrades take effect at next billing cycle.
""",
    "billing": """
Billing FAQ:
Q: What payment methods do you accept?
A: Credit cards (Visa, Mastercard, Amex), PayPal, and wire transfer for Enterprise.

Q: How do I get a refund?
A: Contact support within 30 days of purchase for a full refund.

Q: Where can I find my invoices?
A: Dashboard > Settings > Billing > Invoice History
""",
    "security": """
Security FAQ:
Q: Is my data encrypted?
A: Yes, all data is encrypted at rest (AES-256) and in transit (TLS 1.3).

Q: Do you have SOC 2 compliance?
A: Yes, we are SOC 2 Type II certified. Reports available for Enterprise customers.

Q: How do you handle data breaches?
A: We follow a strict incident response process and notify affected users within 72 hours.
""",
}

TUTORIAL_KNOWLEDGE = {
    "quickstart": """
Quickstart Tutorial (5 minutes):

1. Sign up at https://example.com/signup
2. Create your first project in the dashboard
3. Generate an API key (Settings > API Keys > Create)
4. Install our SDK: pip install example-sdk
5. Initialize the client:
   ```python
   from example import Client
   client = Client(api_key="your-key")
   ```
6. Make your first API call:
   ```python
   users = client.users.list()
   print(users)
   ```

Congratulations! You're ready to build.
""",
    "webhooks": """
Webhooks Tutorial:

Setting up webhooks to receive real-time events:

1. Go to Dashboard > Settings > Webhooks
2. Click "Add Endpoint"
3. Enter your endpoint URL (must be HTTPS)
4. Select events to subscribe to:
   - user.created
   - user.updated
   - payment.completed
5. Copy the signing secret for verification

Verify webhooks in your code:
```python
import hmac
def verify_webhook(payload, signature, secret):
    expected = hmac.new(secret.encode(), payload, 'sha256').hexdigest()
    return hmac.compare_digest(expected, signature)
```
""",
    "deployment": """
Deployment Guide:

Deploying to production:

1. Environment Setup
   - Set NODE_ENV=production
   - Configure DATABASE_URL for production database
   - Set API_KEY from production credentials

2. Docker Deployment
   ```
   docker build -t myapp .
   docker run -p 8080:8080 myapp
   ```

3. Kubernetes (recommended for scale)
   - Use our Helm chart: helm install myapp ./charts/myapp
   - Configure HPA for auto-scaling
   - Set up liveness/readiness probes

4. Monitoring
   - Enable APM integration in dashboard
   - Configure alerts for error rate > 1%
""",
}


@tool
def search_docs(query: str, section: str = "all") -> str:
    """Search technical documentation.

    Args:
        query: Search query
        section: Specific section to search - "api_authentication", "api_endpoints", "database_schema", or "all"
    """
    if section != "all" and section in DOCS_KNOWLEDGE:
        return DOCS_KNOWLEDGE[section]

    # Search all sections for relevant content
    results = []
    query_lower = query.lower()
    for key, content in DOCS_KNOWLEDGE.items():
        if any(word in content.lower() for word in query_lower.split()):
            results.append(f"[{key}]\n{content}")

    return "\n\n".join(results) if results else "No relevant documentation found."


@tool
def search_faq(query: str, category: str = "all") -> str:
    """Search frequently asked questions.

    Args:
        query: Search query
        category: Specific category - "pricing", "billing", "security", or "all"
    """
    if category != "all" and category in FAQ_KNOWLEDGE:
        return FAQ_KNOWLEDGE[category]

    # Search all FAQs
    results = []
    query_lower = query.lower()
    for key, content in FAQ_KNOWLEDGE.items():
        if any(word in content.lower() for word in query_lower.split()):
            results.append(f"[{key}]\n{content}")

    return "\n\n".join(results) if results else "No relevant FAQ found."


@tool
def search_tutorials(query: str, topic: str = "all") -> str:
    """Search tutorial guides.

    Args:
        query: Search query
        topic: Specific topic - "quickstart", "webhooks", "deployment", or "all"
    """
    if topic != "all" and topic in TUTORIAL_KNOWLEDGE:
        return TUTORIAL_KNOWLEDGE[topic]

    # Search all tutorials
    results = []
    query_lower = query.lower()
    for key, content in TUTORIAL_KNOWLEDGE.items():
        if any(word in content.lower() for word in query_lower.split()):
            results.append(f"[{key}]\n{content}")

    return "\n\n".join(results) if results else "No relevant tutorial found."
