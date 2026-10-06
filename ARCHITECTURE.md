# Floresis OpsPilot AI — Architecture

Browser → FastAPI REST API → service layer → SQLAlchemy → relational database.

The repository defaults to SQLite for a zero-setup demo. Production evolution: PostgreSQL, Redis-backed queues, object storage, OpenTelemetry, managed secrets, CI/CD, and horizontal workers. AI/ML logic is isolated behind services so external models can replace deterministic demo engines without rewriting API routes.

## Engineering decisions
- API-first design with typed Pydantic contracts.
- Deterministic local intelligence so reviewers can run the project without paid keys.
- Persistence for auditable demonstrations.
- Health endpoint, automated tests, Docker image, seed data, and OpenAPI docs.
