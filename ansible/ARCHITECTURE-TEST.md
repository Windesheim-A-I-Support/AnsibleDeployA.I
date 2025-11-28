# Test AI Stack - Distributed Architecture Design

## Executive Summary
This document outlines a scalable, multi-container architecture for the test AI stack (10.0.6.x network) designed for multi-user environments where services require per-user isolation.

---

## Scaling Analysis

### Services Requiring Per-User Isolation

#### 1. **n8n** (Workflow Automation)
- **Limitation**: One container = One account
- **Reason**: Single-tenant authentication, workflow isolation
- **Solution**: Deploy one n8n container per user
- **Resource Impact**: Medium (CPU/RAM per instance)

#### 2. **Open WebUI** (Chat Interface)
- **Limitation**: One container = One OpenRouter API key
- **Reason**: Global API key configuration, no per-user key support
- **Solution**: Deploy one Open WebUI container per user
- **Resource Impact**: Low (lightweight Node.js app)

#### 3. **Flowise** (Low-code AI)
- **Limitation**: Single admin account per instance
- **Reason**: Authentication system similar to n8n
- **Solution**: Deploy one Flowise container per user
- **Resource Impact**: Low-Medium

---

### Shared Infrastructure Services (Multi-tenant)

#### 1. **Ollama** (LLM Inference)
- **Scalability**: Multi-tenant capable
- **Reason**: Stateless inference, handles concurrent requests
- **Solution**: Single shared instance (can scale horizontally if needed)
- **Resource Impact**: High (CPU/RAM for model loading)

#### 2. **Qdrant** (Vector Database)
- **Scalability**: Multi-tenant capable with collections
- **Reason**: Each user can have separate collections
- **Solution**: Single shared instance
- **Resource Impact**: Medium (RAM for vectors)

#### 3. **PostgreSQL** (Relational Database)
- **Scalability**: Multi-tenant capable with schemas/databases
- **Reason**: Each service can have separate database
- **Solution**: Single shared instance
- **Resource Impact**: Medium

#### 4. **Langfuse** (LLM Observability)
- **Scalability**: Multi-tenant with projects
- **Reason**: Supports multiple projects/API keys
- **Solution**: Single shared instance
- **Resource Impact**: Low-Medium

#### 5. **SearXNG** (Search Aggregation)
- **Scalability**: Multi-tenant capable
- **Reason**: Stateless search proxy
- **Solution**: Single shared instance
- **Resource Impact**: Low

#### 6. **MinIO** (Object Storage)
- **Scalability**: Multi-tenant with buckets
- **Reason**: Bucket-based isolation
- **Solution**: Single shared instance
- **Resource Impact**: Storage-dependent

#### 7. **Neo4j** (Graph Database)
- **Scalability**: Multi-tenant with databases (Enterprise) or single-tenant (Community)
- **Reason**: Community edition = single database
- **Solution**: Single shared instance for now (evaluate per-user if needed)
- **Resource Impact**: Medium-High

#### 8. **Supabase** (Backend Services)
- **Scalability**: Multi-tenant capable
- **Reason**: Row-level security, user authentication built-in
- **Solution**: Single shared instance
- **Resource Impact**: Medium-High

---

## Proposed Architecture

### Container Layout (10.0.6.x Network)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Traefik Reverse Proxy (10.0.4.10)                 │
│              test-*.valuechainhackers.xyz                            │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTPS
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SHARED INFRASTRUCTURE                            │
│                     Container: 10.0.6.10                             │
├─────────────────────────────────────────────────────────────────────┤
│  - Ollama (11434)           - High resource usage                    │
│  - Qdrant (6333)            - Shared vector storage                  │
│  - PostgreSQL (5432)        - Shared DB for all services             │
│  - Langfuse (3002)          - Shared observability                   │
│  - SearXNG (8081)           - Shared search                          │
│  - MinIO (9000, 9011)       - Shared object storage                  │
│  - Neo4j (7474, 7687)       - Shared graph database                  │
│  - Supabase (8000)          - Shared backend services                │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   USER 1 SERVICES   │  │   USER 2 SERVICES   │  │   USER 3 SERVICES   │
│   Container 10.0.6.11│  │   Container 10.0.6.12│  │   Container 10.0.6.13│
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ - Open WebUI (3000) │  │ - Open WebUI (3000) │  │ - Open WebUI (3000) │
│   → Ollama @ 10.0.6.10│ │   → Ollama @ 10.0.6.10│ │   → Ollama @ 10.0.6.10│
│   → Qdrant @ 10.0.6.10│ │   → Qdrant @ 10.0.6.10│ │   → Qdrant @ 10.0.6.10│
│                     │  │                     │  │                     │
│ - n8n (5678)        │  │ - n8n (5678)        │  │ - n8n (5678)        │
│   → Ollama @ 10.0.6.10│ │   → Ollama @ 10.0.6.10│ │   → Ollama @ 10.0.6.10│
│   → PostgreSQL      │  │   → PostgreSQL      │  │   → PostgreSQL      │
│     @ 10.0.6.10     │  │     @ 10.0.6.10     │  │     @ 10.0.6.10     │
│                     │  │                     │  │                     │
│ - Flowise (3001)    │  │ - Flowise (3001)    │  │ - Flowise (3001)    │
│   → Ollama @ 10.0.6.10│ │   → Ollama @ 10.0.6.10│ │   → Ollama @ 10.0.6.10│
│   → Qdrant @ 10.0.6.10│ │   → Qdrant @ 10.0.6.10│ │   → Qdrant @ 10.0.6.10│
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

### Domain Mapping

#### Shared Infrastructure (10.0.6.10)
- `test-ollama.valuechainhackers.xyz` → 10.0.6.10:11434
- `test-qdrant.valuechainhackers.xyz` → 10.0.6.10:6333
- `test-langfuse.valuechainhackers.xyz` → 10.0.6.10:3002
- `test-searxng.valuechainhackers.xyz` → 10.0.6.10:8081
- `test-minio.valuechainhackers.xyz` → 10.0.6.10:9011
- `test-neo4j.valuechainhackers.xyz` → 10.0.6.10:7474
- `test-supabase.valuechainhackers.xyz` → 10.0.6.10:8000

#### User 1 Services (10.0.6.11)
- `test-user1-openwebui.valuechainhackers.xyz` → 10.0.6.11:3000
- `test-user1-n8n.valuechainhackers.xyz` → 10.0.6.11:5678
- `test-user1-flowise.valuechainhackers.xyz` → 10.0.6.11:3001

#### User 2 Services (10.0.6.12)
- `test-user2-openwebui.valuechainhackers.xyz` → 10.0.6.12:3000
- `test-user2-n8n.valuechainhackers.xyz` → 10.0.6.12:5678
- `test-user2-flowise.valuechainhackers.xyz` → 10.0.6.12:3001

#### User 3 Services (10.0.6.13)
- `test-user3-openwebui.valuechainhackers.xyz` → 10.0.6.13:3000
- `test-user3-n8n.valuechainhackers.xyz` → 10.0.6.13:5678
- `test-user3-flowise.valuechainhackers.xyz` → 10.0.6.13:3001

---

## Container Specifications

### Shared Infrastructure Container (10.0.6.10)
**LXC Configuration:**
```
CPU: 8 cores
RAM: 16GB
Storage: 100GB
Features: nesting=1, keyctl=1
```

**Services:**
- Ollama (CPU profile): ~4GB RAM, 4 cores
- Qdrant: ~2GB RAM
- PostgreSQL: ~2GB RAM
- Langfuse: ~1GB RAM
- SearXNG: ~512MB RAM
- MinIO: ~1GB RAM
- Neo4j: ~2GB RAM
- Supabase stack: ~3GB RAM

### Per-User Containers (10.0.6.11, 10.0.6.12, 10.0.6.13)
**LXC Configuration:**
```
CPU: 2 cores
RAM: 4GB
Storage: 20GB
Features: nesting=1
```

**Services:**
- Open WebUI: ~512MB RAM
- n8n: ~1GB RAM
- Flowise: ~1GB RAM

---

## Data Isolation Strategy

### PostgreSQL Database Isolation
```sql
-- Shared infrastructure database
CREATE DATABASE shared_langfuse;
CREATE DATABASE shared_supabase;

-- Per-user databases
CREATE DATABASE user1_n8n;
CREATE DATABASE user1_flowise;

CREATE DATABASE user2_n8n;
CREATE DATABASE user2_flowise;

CREATE DATABASE user3_n8n;
CREATE DATABASE user3_flowise;
```

### Qdrant Collection Isolation
```
user1_openwebui_documents
user1_flowise_vectors

user2_openwebui_documents
user2_flowise_vectors

user3_openwebui_documents
user3_flowise_vectors
```

### MinIO Bucket Isolation
```
user1-uploads
user1-backups

user2-uploads
user2-backups

user3-uploads
user3-backups
```

---

## Environment Configuration

### Shared Infrastructure (.env)
```bash
# PostgreSQL (shared)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<generated>
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Ollama (shared)
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_ORIGINS=*

# Qdrant (shared)
QDRANT_HOST=0.0.0.0
QDRANT_PORT=6333

# Langfuse (shared)
LANGFUSE_PORT=3002
LANGFUSE_DATABASE_URL=postgresql://postgres:<pass>@db:5432/shared_langfuse

# MinIO (shared)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=<generated>

# Neo4j (shared)
NEO4J_AUTH=neo4j/<generated>
```

### User 1 Container (.env)
```bash
# Open WebUI
OPENWEBUI_PORT=3000
OLLAMA_BASE_URL=http://10.0.6.10:11434
QDRANT_URI=http://10.0.6.10:6333
VECTOR_DB=qdrant
OPENWEBUI_COLLECTION_NAME=user1_openwebui_documents
OPENROUTER_API_KEY=<user1_key>

# n8n
N8N_PORT=5678
N8N_ENCRYPTION_KEY=<generated>
N8N_USER_MANAGEMENT_JWT_SECRET=<generated>
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=10.0.6.10
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=user1_n8n
DB_POSTGRESDB_USER=postgres
DB_POSTGRESDB_PASSWORD=<shared_postgres_pass>

# Flowise
FLOWISE_PORT=3001
FLOWISE_DATABASE_TYPE=postgres
FLOWISE_DATABASE_HOST=10.0.6.10
FLOWISE_DATABASE_PORT=5432
FLOWISE_DATABASE_NAME=user1_flowise
FLOWISE_DATABASE_USER=postgres
FLOWISE_DATABASE_PASSWORD=<shared_postgres_pass>
```

---

## Scaling Considerations

### Adding New Users
1. Provision new LXC container (10.0.6.X)
2. Deploy user services (Open WebUI, n8n, Flowise)
3. Create isolated databases in shared PostgreSQL
4. Create isolated collections in shared Qdrant
5. Add Traefik routing configuration
6. Configure unique OpenRouter API key

### Horizontal Scaling of Shared Services

#### Ollama Scaling
- Deploy multiple Ollama instances (10.0.6.10, 10.0.6.20)
- Use Traefik load balancing across instances
- Share model cache via NFS

#### Qdrant Scaling
- Enable Qdrant clustering
- Distribute collections across nodes

#### PostgreSQL Scaling
- Implement read replicas
- Consider connection pooling (PgBouncer)

---

## Deployment Strategy

### Phase 1: Shared Infrastructure
1. Deploy container 10.0.6.10
2. Install Docker
3. Deploy shared services:
   - PostgreSQL
   - Ollama (with models)
   - Qdrant
   - Langfuse
   - SearXNG
   - MinIO
   - Neo4j
   - Supabase

### Phase 2: User 1 Services
1. Deploy container 10.0.6.11
2. Install Docker
3. Deploy user services (Open WebUI, n8n, Flowise)
4. Configure connections to shared infrastructure
5. Create databases/collections/buckets
6. Configure Traefik routing

### Phase 3: Additional Users (Repeatable)
1. Clone container configuration
2. Update IP address (10.0.6.12, 10.0.6.13)
3. Update domain prefixes (user2, user3)
4. Update API keys and credentials
5. Repeat Phase 2 steps

---

## Future Enhancements

### Authentication & SSO
- Deploy Authentik or Keycloak on shared infrastructure
- Implement single sign-on across all user services
- Use LDAP/SAML for centralized user management

### Service Mesh
- Implement Linkerd or Istio for service-to-service communication
- Automatic mTLS between containers
- Distributed tracing across all services

### Monitoring
- Deploy Prometheus on shared infrastructure
- Collect metrics from all containers
- Grafana dashboards for per-user resource usage

### Backup Strategy
- Automated nightly backups of PostgreSQL databases
- Qdrant collection snapshots
- MinIO bucket replication
- User service configuration backups

---

## Cost-Benefit Analysis

### Advantages of Distributed Architecture
- **Isolation**: User API keys and workflows completely isolated
- **Scalability**: Easy to add new users without affecting existing ones
- **Resource Efficiency**: Heavy services (Ollama, Qdrant) shared across users
- **Flexibility**: Users can have different versions/configs
- **Fault Tolerance**: User service failure doesn't affect others

### Disadvantages
- **Complexity**: More containers to manage
- **Resource Overhead**: Each user container has base overhead
- **Network Latency**: Cross-container communication adds latency
- **Management**: More Traefik configurations to maintain

### Resource Comparison

**Monolithic (Single Container per User)**
- User 1: 16GB RAM (includes Ollama, Qdrant, etc.)
- User 2: 16GB RAM
- User 3: 16GB RAM
- **Total: 48GB RAM**

**Distributed Architecture**
- Shared Infrastructure: 16GB RAM
- User 1: 4GB RAM
- User 2: 4GB RAM
- User 3: 4GB RAM
- **Total: 28GB RAM (42% savings)**

---

**Document Version**: 1.0
**Last Updated**: 2025-11-24
**Author**: Infrastructure Design
**Status**: Proposed Architecture
