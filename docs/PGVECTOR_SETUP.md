# pgvector Installation Guide

pgvector is required for vector similarity search (RIYL feature).

## Installation Steps (requires sudo)

```bash
# For Ubuntu/Debian with PostgreSQL 18
sudo apt-get update
sudo apt-get install -y postgresql-18-pgvector

# Or build from source if package not available:
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

## Enable Extension

```bash
psql -d tunescore -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Verification

```bash
psql -d tunescore -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

## Alternative: Use PostgreSQL Arrays

If pgvector cannot be installed, we can use PostgreSQL arrays for embeddings
with custom cosine similarity functions. Performance will be slower but functional.
