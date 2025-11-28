# Service Categorization for Distributed AI Stack

## Overview
This document categorizes all 90+ services from Extra Services into deployment tiers based on multi-tenancy capability, resource requirements, and integration patterns.

---

## Deployment Tiers

### 🔴 TIER 1: SHARED INFRASTRUCTURE (10.0.6.10)
**Multi-tenant capable services that should be deployed once and shared across all users**

#### Core AI Services
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **Ollama** | 11434 | ✅ Yes | API Key (optional) | All AI frontends |
| **Qdrant** | 6333 | ✅ Yes (collections) | API Key | Open WebUI, Flowise, n8n |
| **PostgreSQL** | 5432 | ✅ Yes (databases) | User/Pass per DB | n8n, Flowise, Langfuse, Supabase |
| **Neo4j** | 7474, 7687 | ✅ Yes (databases) | User/Pass | Knowledge graphs, n8n |
| **MinIO** | 9000, 9011 | ✅ Yes (buckets) | Access/Secret Key | Langfuse, Supabase, backup storage |

#### Observability & Monitoring
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **Langfuse** | 3002 | ✅ Yes (projects) | Project API keys | Open WebUI, n8n, Flowise (via SDK) |
| **Grafana** | 3100 | ✅ Yes (organizations) | User/Pass | Prometheus, Loki |
| **Prometheus** | 9090 | ✅ Yes (labels) | None/Basic Auth | All containers (exporters) |
| **Loki** | 3100 | ✅ Yes (labels) | None/Basic Auth | All containers (Promtail) |
| **Uptime Kuma** | 3201 | ✅ Yes (users) | User/Pass | Monitor all services |
| **Dozzle** | 8080 | ⚠️ Read-only | None | View Docker logs |
| **PostHog** | 8001 | ✅ Yes (projects) | Project API Key | Open WebUI analytics |
| **Plausible** | 8002 | ✅ Yes (sites) | User/Pass | Web analytics |

#### Search & Discovery
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **SearXNG** | 8081 | ✅ Yes | None | Open WebUI, n8n |
| **Meilisearch** | 7700 | ✅ Yes (indexes) | Master/Search keys | Document search, n8n |
| **Typesense** | 8108 | ✅ Yes (collections) | API Key | Alternative to Meilisearch |

#### AI Utilities
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **Apache Tika** | 9998 | ✅ Yes | None | Document parsing for RAG |
| **Gotenberg** | 3003 | ✅ Yes | None | PDF generation from HTML/Markdown |
| **Piston** | 2000 | ✅ Yes | None | Code execution (n8n, Open WebUI) |
| **Browserless** | 3000 | ✅ Yes | Token | Web scraping (n8n) |
| **AllTalk** | 7851 | ✅ Yes | None | TTS for Open WebUI |
| **Whisper** | 9000 | ✅ Yes | None | STT for Open WebUI |
| **Stirling-PDF** | 8088 | ✅ Yes | None | PDF manipulation |

#### Backend Services
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **Supabase** | 8000 | ✅ Yes (projects/RLS) | JWT tokens | All apps needing backend |
| **LiteLLM** | 4000 | ✅ Yes (keys) | API Key | Load balance LLM providers |

#### Data & Analytics
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **Metabase** | 3003 | ✅ Yes (users) | User/Pass | PostgreSQL dashboards |
| **Apache Superset** | 8088 | ✅ Yes (users/RBAC) | User/Pass | Advanced BI dashboards |
| **Redash** | 5000 | ✅ Yes (users) | User/Pass | SQL queries & dashboards |
| **Druid** | 8888 | ✅ Yes (tables) | None/Basic Auth | Real-time analytics |

#### Workflow Orchestration (Shared)
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **Apache Airflow** | 8080 | ⚠️ Limited (DAGs) | User/Pass | Data pipelines |
| **Dagster** | 3000 | ⚠️ Limited | User/Pass | Alternative to Airflow |
| **Prefect** | 4200 | ✅ Yes (workspaces) | User/Pass | Modern workflow engine |
| **Kestra** | 8080 | ✅ Yes (tenants) | User/Pass | Event-driven workflows |

#### DevOps & Management
| Service | Port | Multi-Tenant | Auth Strategy | Integration Points |
|---------|------|--------------|---------------|-------------------|
| **Portainer** | 9443 | ✅ Yes (users/teams) | User/Pass | Docker management UI |
| **Watchtower** | - | ✅ Yes | None | Auto-update containers |

---

### 🟡 TIER 2: PER-USER SERVICES (10.0.6.11, 10.0.6.12, 10.0.6.13...)
**Services requiring user isolation due to single-tenant limitations**

#### AI Frontends (User-specific)
| Service | Port | Why Per-User | Resource | Connects To |
|---------|------|--------------|----------|-------------|
| **Open WebUI** | 3000 | Single OpenRouter key, user preferences | Low | Ollama, Qdrant, Langfuse (10.0.6.10) |
| **Flowise** | 3001 | Single admin account | Low-Med | Ollama, Qdrant, PostgreSQL (10.0.6.10) |
| **n8n** | 5678 | Single account, workflow isolation | Med | Ollama, PostgreSQL, all APIs (10.0.6.10) |
| **Dify** | 3005 | Single workspace | Low-Med | Ollama, Qdrant (10.0.6.10) |
| **Anything LLM** | 3001 | Workspace isolation | Low | Ollama, Qdrant (10.0.6.10) |
| **Text Generation WebUI** | 7860 | Model-specific configs | Med-High | Dedicated LLM models |

#### Workflow Automation (User-specific)
| Service | Port | Why Per-User | Resource | Connects To |
|---------|------|--------------|----------|-------------|
| **Activepieces** | 3000 | Single account | Low-Med | APIs, PostgreSQL (10.0.6.10) |
| **Trigger.dev** | 3000 | User-specific code | Low | APIs, PostgreSQL (10.0.6.10) |
| **Huginn** | 3000 | Agent-based, single user | Low | Web scraping, APIs |

#### Development Environments (User-specific)
| Service | Port | Why Per-User | Resource | Connects To |
|---------|------|--------------|----------|-------------|
| **JupyterHub** | 8000 | Multi-user but resource isolation needed | High | PostgreSQL, MinIO (10.0.6.10) |
| **RStudio Server** | 8787 | User sessions, package isolation | Med-High | PostgreSQL (10.0.6.10) |
| **Apache Zeppelin** | 8080 | Notebook isolation | Med | PostgreSQL, APIs (10.0.6.10) |

---

### 🟢 TIER 3: OPTIONAL SHARED SERVICES (10.0.6.20)
**Services that enhance functionality but aren't core to AI stack**

#### Knowledge Management
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Outline** | 3000 | ✅ Yes (teams) | SSO/User | ✅ Deploy (shared docs) |
| **Wiki.js** | 3000 | ✅ Yes (users) | User/Pass | ✅ Deploy (technical docs) |
| **BookStack** | 3000 | ✅ Yes (users) | User/Pass | ⚠️ Skip (Outline better) |
| **Memos** | 5230 | ⚠️ Limited | User/Pass | ⚠️ Per-user or skip |
| **Paperless-ngx** | 8000 | ⚠️ Limited | User/Pass | ⚠️ Per-user recommended |
| **Calibre-Web** | 8083 | ⚠️ Limited | User/Pass | ⚠️ Per-user or skip |

#### Research & Lab Tools
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **eLabFTW** | 443 | ✅ Yes (teams) | User/Pass | ✅ Deploy (lab notebook) |
| **Label Studio** | 8080 | ✅ Yes (projects) | User/Pass | ✅ Deploy (data labeling) |
| **OpenRefine** | 3333 | ⚠️ Limited | None | ⚠️ Per-user |

#### File Management
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Nextcloud** | 443 | ✅ Yes (users) | User/Pass | ✅ Deploy (file sync) |
| **Seafile** | 8000 | ✅ Yes (users) | User/Pass | ⚠️ Skip (Nextcloud sufficient) |

#### Version Control & DevOps
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Gitea** | 3000 | ✅ Yes (users/orgs) | User/Pass | ✅ Deploy (Git server) |

#### Project Management
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Kanboard** | 80 | ✅ Yes (users) | User/Pass | ✅ Deploy (project tracking) |

#### Communication
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Mattermost** | 8065 | ✅ Yes (users/teams) | User/Pass | ✅ Deploy (team chat) |
| **Rocket.Chat** | 3000 | ✅ Yes (users) | User/Pass | ⚠️ Skip (Mattermost better) |
| **Zulip** | 9991 | ✅ Yes (users) | User/Pass | ⚠️ Skip (Mattermost sufficient) |
| **Cal.com** | 3000 | ✅ Yes (users) | User/Pass | ✅ Deploy (scheduling) |
| **Jitsi Meet** | 8443 | ✅ Yes | None/JWT | ✅ Deploy (video calls) |

#### Mail Server
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Docker-Mailserver** | 25, 587, 993 | ✅ Yes (accounts) | User/Pass | ✅ Deploy (full SMTP/IMAP server) |
| **Maddy** | 25, 587, 993 | ✅ Yes (accounts) | User/Pass | ⚠️ Alternative (simpler) |
| **Mailu** | 80, 25, 587, 993 | ✅ Yes (accounts) | User/Pass | ⚠️ Skip (Docker-Mailserver more flexible) |

#### Forms & Surveys
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Formbricks** | 3000 | ✅ Yes (projects) | User/Pass | ✅ Deploy (user research & surveys) |
| **LimeSurvey** | 80 | ✅ Yes (users) | User/Pass | ⚠️ Skip (Formbricks more modern) |

#### Utilities
| Service | Port | Multi-Tenant | Auth | Decision |
|---------|------|--------------|------|----------|
| **Draw.io** | 8080 | ⚠️ Limited | None | ⚠️ Per-user or skip |
| **ChangeDetection.io** | 5000 | ⚠️ Limited | User/Pass | ⚠️ Per-user |

---

### 🔵 TIER 4: OPTIONAL PER-USER SERVICES
**Services that could be deployed per-user if needed**

#### Image Generation (Resource-Intensive)
| Service | Port | Multi-Tenant | Resource | Decision |
|---------|------|--------------|----------|----------|
| **ComfyUI** | 8188 | ⚠️ Limited | High (CPU/GPU) | ⚠️ Per-user if needed |
| **Stable Diffusion WebUI** | 7860 | ⚠️ Limited | Very High (GPU) | ❌ Skip (too resource-heavy for CPU) |
| **InvokeAI** | 9090 | ⚠️ Limited | Very High (GPU) | ❌ Skip (GPU required) |
| **Kohya_ss** | 7860 | ❌ No | Very High (GPU) | ❌ Skip (GPU training) |

#### Voice Services (Per-user recommended)
| Service | Port | Multi-Tenant | Resource | Decision |
|---------|------|--------------|----------|----------|
| **Coqui TTS** | 5002 | ⚠️ Limited | Med | ⚠️ Shared or skip (AllTalk sufficient) |
| **OpenVoice** | 5000 | ⚠️ Limited | Med | ⚠️ Skip (AllTalk sufficient) |

---

### 🔐 TIER 5: CRITICAL INFRASTRUCTURE (10.0.6.5)
**Authentication, secrets, and security services - deploy first**

| Service | Port | Multi-Tenant | Why Critical | Integrates With |
|---------|------|--------------|--------------|-----------------|
| **Authentik** | 9000, 9443 | ✅ Yes (users/groups) | SSO for all services | All web services |
| **Vaultwarden** | 8080 | ✅ Yes (orgs) | Password management | All services (credential storage) |
| **Authelia** | 9091 | ✅ Yes | 2FA/SSO via proxy | Traefik, all services |

**Decision**: Deploy **Authentik** as primary SSO provider. All services should authenticate through Authentik.

---

## Recommended Deployment Configuration

### Container 1: Critical Infrastructure (10.0.6.5)
**Priority: Deploy First**
- Authentik (SSO)
- Vaultwarden (Passwords)
- Authelia (2FA/SSO Proxy)

**Resources**: 4GB RAM, 2 CPU cores

---

### Container 2: Shared AI Infrastructure (10.0.6.10)
**Priority: Deploy Second**

#### Core AI Services
- Ollama (4GB RAM, 4 cores)
- Qdrant (2GB RAM)
- PostgreSQL (2GB RAM)
- Neo4j (2GB RAM)
- MinIO (1GB RAM)

#### AI Utilities
- Langfuse (1GB RAM)
- SearXNG (512MB RAM)
- Apache Tika (512MB RAM)
- Gotenberg (512MB RAM)
- Piston (512MB RAM)
- Browserless (1GB RAM)
- AllTalk (1GB RAM)
- Whisper (2GB RAM)
- Stirling-PDF (512MB RAM)
- LiteLLM (512MB RAM)

#### Search
- Meilisearch (1GB RAM)

#### Supabase Stack
- Supabase services (3GB RAM)

**Total Resources**: 20GB RAM, 8 CPU cores

---

### Container 3: Monitoring & DevOps (10.0.6.15)
**Priority: Deploy Third**

- Grafana (512MB RAM)
- Prometheus (2GB RAM)
- Loki (1GB RAM)
- Uptime Kuma (512MB RAM)
- Portainer (512MB RAM)
- Dozzle (256MB RAM)
- Watchtower (256MB RAM)
- PostHog (2GB RAM)
- Plausible (512MB RAM)

**Total Resources**: 8GB RAM, 4 CPU cores

---

### Container 4: Collaboration & Knowledge (10.0.6.20)
**Priority: Deploy Fourth**

- Outline (1GB RAM)
- Wiki.js (1GB RAM)
- eLabFTW (1GB RAM)
- Label Studio (1GB RAM)
- Nextcloud (2GB RAM)
- Gitea (1GB RAM)
- Kanboard (512MB RAM)
- Mattermost (2GB RAM)
- Cal.com (512MB RAM)
- Jitsi Meet (2GB RAM)

**Total Resources**: 12GB RAM, 4 CPU cores

---

### Container 5: Data & Analytics (10.0.6.25)
**Priority: Deploy Fifth (Optional)**

- Metabase (2GB RAM)
- Apache Superset (2GB RAM)
- Prefect (1GB RAM)
- Redash (1GB RAM)

**Total Resources**: 6GB RAM, 2 CPU cores

---

### Containers 10.0.6.11, 10.0.6.12, 10.0.6.13... : Per-User Services
**Priority: Deploy per user as needed**

Each user container:
- Open WebUI (512MB RAM)
- n8n (1GB RAM)
- Flowise (1GB RAM)
- JupyterHub (2GB RAM) - optional
- RStudio Server (2GB RAM) - optional

**Base Resources per User**: 4GB RAM, 2 CPU cores
**With Development Tools**: 8GB RAM, 4 CPU cores

---

## Authentication & Integration Strategy

### Single Sign-On (SSO) Configuration

#### Authentik Setup
```yaml
# Authentik will be configured with:
- LDAP Provider for legacy apps
- OAuth2/OIDC for modern apps
- SAML for enterprise integration
- Groups: admin, researcher, user
- MFA enforced for all users
```

#### Service Integration with Authentik

| Service | Auth Method | SSO Config |
|---------|-------------|------------|
| Open WebUI | OAuth2 | ✅ Supported |
| n8n | OAuth2 | ✅ Supported |
| Flowise | Basic Auth → Authelia | ⚠️ Via proxy |
| Grafana | OAuth2 | ✅ Supported |
| Nextcloud | LDAP | ✅ Supported |
| Gitea | OAuth2 | ✅ Supported |
| Mattermost | SAML/OAuth2 | ✅ Supported |
| Outline | OAuth2 | ✅ Supported |
| Wiki.js | OAuth2 | ✅ Supported |
| JupyterHub | OAuth2 | ✅ Supported |
| Portainer | OAuth2 | ✅ Supported |

---

### Password Synchronization Strategy

#### Vaultwarden Integration
```
1. All service credentials stored in Vaultwarden
2. Organized by collections:
   - Infrastructure (Postgres, Neo4j, etc.)
   - User Services (per-user OpenRouter keys)
   - API Keys (Langfuse, OpenAI, etc.)
3. CLI access via `bw` for automation
4. Ansible retrieves secrets during deployment
```

#### Secret Management Flow
```
┌─────────────────┐
│   Vaultwarden   │ ← Master password vault
└────────┬────────┘
         │
         ├─→ Ansible Playbooks (retrieves secrets)
         │
         ├─→ User Browsers (Bitwarden extension)
         │
         └─→ CI/CD (via API keys)
```

---

## Service Communication Matrix

### Open WebUI Integration
```yaml
Connects to:
  - Ollama (10.0.6.10:11434) - LLM inference
  - Qdrant (10.0.6.10:6333) - Vector storage
  - Langfuse (10.0.6.10:3002) - Observability
  - SearXNG (10.0.6.10:8081) - Web search
  - Whisper (10.0.6.10:9000) - Speech-to-text
  - AllTalk (10.0.6.10:7851) - Text-to-speech
  - Piston (10.0.6.10:2000) - Code execution
  - Apache Tika (10.0.6.10:9998) - Document parsing
  - Authentik (10.0.6.5:9000) - SSO authentication

Environment Variables:
  - OLLAMA_BASE_URL=http://10.0.6.10:11434
  - VECTOR_DB=qdrant
  - QDRANT_URI=http://10.0.6.10:6333
  - QDRANT_COLLECTION=user1_documents
  - LANGFUSE_PUBLIC_KEY=<from_vaultwarden>
  - LANGFUSE_SECRET_KEY=<from_vaultwarden>
  - LANGFUSE_HOST=http://10.0.6.10:3002
  - OAUTH_CLIENT_ID=<authentik_client>
  - OAUTH_CLIENT_SECRET=<from_vaultwarden>
```

### n8n Integration
```yaml
Connects to:
  - PostgreSQL (10.0.6.10:5432) - Workflow storage
  - Ollama (10.0.6.10:11434) - AI actions
  - Browserless (10.0.6.10:3000) - Web scraping
  - Gotenberg (10.0.6.10:3003) - PDF generation
  - Meilisearch (10.0.6.10:7700) - Search indexing
  - MinIO (10.0.6.10:9000) - File storage
  - Mattermost (10.0.6.20:8065) - Notifications
  - Authentik (10.0.6.5:9000) - SSO

Environment Variables:
  - DB_TYPE=postgresdb
  - DB_POSTGRESDB_HOST=10.0.6.10
  - DB_POSTGRESDB_DATABASE=user1_n8n
  - DB_POSTGRESDB_PASSWORD=<from_vaultwarden>
  - NODE_FUNCTION_ALLOW_EXTERNAL=*
  - N8N_ENCRYPTION_KEY=<generated_per_user>
```

### Flowise Integration
```yaml
Connects to:
  - PostgreSQL (10.0.6.10:5432) - Flow storage
  - Ollama (10.0.6.10:11434) - LLM node
  - Qdrant (10.0.6.10:6333) - Vector store node
  - Apache Tika (10.0.6.10:9998) - Document loader
  - Browserless (10.0.6.10:3000) - Web scraper node
  - Langfuse (10.0.6.10:3002) - Observability
  - Authentik (10.0.6.5:9000) - SSO

Environment Variables:
  - FLOWISE_DATABASE_TYPE=postgres
  - FLOWISE_DATABASE_HOST=10.0.6.10
  - FLOWISE_DATABASE_NAME=user1_flowise
  - FLOWISE_DATABASE_PASSWORD=<from_vaultwarden>
```

---

## Deployment Priority Matrix

### Phase 1: Foundation (Week 1)
1. ✅ Deploy Traefik (already exists at 10.0.4.10)
2. Deploy Authentik (10.0.6.5)
3. Deploy Vaultwarden (10.0.6.5)
4. Configure Traefik → Authentik integration

### Phase 2: Core AI Infrastructure (Week 1-2)
1. Deploy Container 10.0.6.10 (Shared AI services)
2. Configure PostgreSQL databases
3. Configure Qdrant collections
4. Pull Ollama models (nomic-embed-text, llama3.2)
5. Configure Langfuse projects

### Phase 3: Monitoring (Week 2)
1. Deploy Container 10.0.6.15 (Monitoring)
2. Configure Prometheus scraping
3. Setup Grafana dashboards
4. Configure Uptime Kuma monitors
5. Setup alerts

### Phase 4: First User Deployment (Week 2)
1. Deploy Container 10.0.6.11 (User 1)
2. Configure Open WebUI → all integrations
3. Configure n8n → PostgreSQL, Ollama
4. Configure Flowise → all integrations
5. Test SSO login via Authentik
6. Verify all service connections

### Phase 5: Collaboration Tools (Week 3)
1. Deploy Container 10.0.6.20 (Collaboration)
2. Configure Outline, Wiki.js, Gitea
3. Configure Mattermost → Authentik SSO
4. Setup eLabFTW for lab notebooks
5. Configure Nextcloud file sync

### Phase 6: Scale to Additional Users (Week 3+)
1. Clone user container configuration
2. Update IP addresses (10.0.6.12, 10.0.6.13)
3. Generate unique secrets per user
4. Create PostgreSQL databases per user
5. Configure Traefik routing per user
6. Test isolation between users

---

## Resource Summary

### Total Infrastructure Requirements

| Container | IP | RAM | CPU | Storage | Services Count |
|-----------|----|----|-----|---------|----------------|
| Critical Infrastructure | 10.0.6.5 | 4GB | 2 | 20GB | 3 |
| Shared AI | 10.0.6.10 | 20GB | 8 | 100GB | 15 |
| Monitoring | 10.0.6.15 | 8GB | 4 | 50GB | 9 |
| Collaboration | 10.0.6.20 | 12GB | 4 | 100GB | 10 |
| Data Analytics | 10.0.6.25 | 6GB | 2 | 50GB | 4 |
| User 1 | 10.0.6.11 | 4GB | 2 | 20GB | 3 |
| User 2 | 10.0.6.12 | 4GB | 2 | 20GB | 3 |
| User 3 | 10.0.6.13 | 4GB | 2 | 20GB | 3 |

**Total for 3 Users:**
- RAM: 62GB
- CPU: 26 cores
- Storage: 380GB
- Services: 50+

**Comparison to Monolithic (3 users):**
- Monolithic: 48GB RAM (all services duplicated)
- Distributed: 62GB RAM (but with monitoring, analytics, collaboration)
- **Better value with more services for similar resource cost**

---

**Document Version**: 1.0
**Last Updated**: 2025-11-24
**Status**: Service Analysis Complete
**Next Step**: Create Ansible deployment playbooks
