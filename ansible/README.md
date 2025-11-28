# Distributed AI Stack - Ansible Deployment

## Overview
This directory contains Ansible playbooks for deploying a complete, scalable AI stack across multiple LXC containers with proper service isolation and shared infrastructure.

---

## Architecture

### Network Layout (10.0.6.x Test Network)

```
10.0.4.10  - Traefik Reverse Proxy (existing)
10.0.6.5   - Critical Infrastructure (Authentik, Vaultwarden, Authelia)
10.0.6.10  - Shared AI Infrastructure (Ollama, Qdrant, PostgreSQL, etc.)
10.0.6.15  - Monitoring & DevOps (Grafana, Prometheus, Portainer, etc.)
10.0.6.20  - Collaboration & Knowledge (Outline, Wiki.js, Gitea, etc.)
10.0.6.25  - Data & Analytics (Metabase, Superset, Prefect, etc.)
10.0.6.11  - User 1 Services (Open WebUI, n8n, Flowise)
10.0.6.12  - User 2 Services (Open WebUI, n8n, Flowise)
10.0.6.13  - User 3 Services (Open WebUI, n8n, Flowise)
```

---

## Files

### Inventory
- `inventory.yml` - Complete inventory defining all hosts and services

### Architecture Documentation
- `ARCHITECTURE-TEST.md` - Distributed architecture design with container layout
- `SERVICE-CATEGORIZATION.md` - Comprehensive analysis of 90+ services

### Deployment Playbooks
1. `01-deploy-critical-infrastructure.yml` - Deploy Authentik, Vaultwarden, Authelia
2. `02-deploy-shared-ai-infrastructure.yml` - Deploy Ollama, Qdrant, PostgreSQL, etc.
3. `03-deploy-monitoring.yml` - Deploy Grafana, Prometheus, Uptime Kuma, etc.
4. `04-deploy-collaboration.yml` - Deploy Outline, Wiki.js, Mattermost, etc.
5. `05-deploy-analytics.yml` - Deploy Metabase, Superset, Prefect, etc. (optional)
6. `06-deploy-user-services.yml` - Deploy per-user Open WebUI, n8n, Flowise
7. `99-configure-traefik.yml` - Configure Traefik routing for all services

### Templates
- `templates/traefik-*.yml.j2` - Traefik routing configuration templates
- `templates/docker-compose-*.yml.j2` - Service-specific compose files

---

## Prerequisites

### Proxmox LXC Container Requirements

All containers must be created with:
```bash
# Container creation example (10.0.6.5 - Critical Infrastructure)
pct create 605 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname critical-infra-01 \
  --cores 2 \
  --memory 4096 \
  --swap 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.5/24,gw=10.0.5.1 \
  --features nesting=1,keyctl=1 \
  --unprivileged 1 \
  --storage local-lvm \
  --rootfs local-lvm:20

# Start container
pct start 605
```

**Resource Requirements:**
- 10.0.6.5 (Critical): 2 cores, 4GB RAM, 20GB storage
- 10.0.6.10 (Shared AI): 8 cores, 20GB RAM, 100GB storage
- 10.0.6.15 (Monitoring): 4 cores, 8GB RAM, 50GB storage
- 10.0.6.20 (Collaboration): 4 cores, 12GB RAM, 100GB storage
- 10.0.6.25 (Analytics): 2 cores, 6GB RAM, 50GB storage
- 10.0.6.11-13 (Users): 2 cores, 4GB RAM, 20GB storage each

### Ansible Control Node Requirements

```bash
# Install Ansible
sudo apt update
sudo apt install ansible

# Install required collections
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.general

# Install Python dependencies
pip3 install docker docker-compose
```

### SSH Access

Ensure SSH access to all containers:
```bash
# Test connectivity
ansible -i inventory.yml all -m ping

# Expected output:
# critical-infra-01 | SUCCESS => ...
# shared-ai-01 | SUCCESS => ...
# monitoring-01 | SUCCESS => ...
# ...
```

---

## Deployment Process

### Phase 1: Critical Infrastructure (Week 1, Day 1)

Deploy SSO and secrets management:

```bash
ansible-playbook -i inventory.yml 01-deploy-critical-infrastructure.yml
```

**What this deploys:**
- PostgreSQL (for Authentik)
- Redis (for Authentik sessions)
- Authentik (SSO provider)
- Vaultwarden (password manager)
- Authelia (2FA/SSO proxy)

**Post-deployment:**
1. Access Authentik at `http://10.0.6.5:9000`
2. Complete initial setup wizard
3. Create admin user
4. Access Vaultwarden at `http://10.0.6.5:8080`
5. Store all infrastructure secrets in Vaultwarden

**Expected runtime:** 15-20 minutes

---

### Phase 2: Shared AI Infrastructure (Week 1, Day 1-2)

Deploy core AI services:

```bash
ansible-playbook -i inventory.yml 02-deploy-shared-ai-infrastructure.yml
```

**What this deploys:**
- PostgreSQL (shared database)
- Ollama (LLM inference)
- Qdrant (vector database)
- Neo4j (graph database)
- MinIO (object storage)
- Langfuse (LLM observability)
- SearXNG (web search)
- Apache Tika, Gotenberg, Piston (utilities)
- Browserless (web scraping)
- AllTalk, Whisper (voice services)
- Stirling-PDF (PDF manipulation)
- LiteLLM (LLM proxy)
- Meilisearch (search engine)
- Supabase (backend services)

**Post-deployment:**
1. Pull Ollama models: `docker exec ollama ollama pull nomic-embed-text`
2. Create Qdrant collections for users
3. Create PostgreSQL databases for users
4. Configure Langfuse projects

**Expected runtime:** 30-45 minutes

---

### Phase 3: Monitoring (Week 1, Day 2)

Deploy monitoring stack:

```bash
ansible-playbook -i inventory.yml 03-deploy-monitoring.yml
```

**What this deploys:**
- Prometheus (metrics)
- Grafana (dashboards)
- Loki + Promtail (logs)
- Uptime Kuma (uptime monitoring)
- Portainer (Docker management)
- Dozzle (log viewer)
- Watchtower (auto-updates)
- PostHog (product analytics)
- Plausible (web analytics)

**Post-deployment:**
1. Access Grafana at `http://10.0.6.15:3100`
2. Import dashboards for Docker, Prometheus, Ollama
3. Configure Uptime Kuma monitors for all services
4. Setup alert channels (email, Mattermost, Discord)

**Expected runtime:** 20-30 minutes

---

### Phase 4: Collaboration Tools (Week 2, Day 1)

Deploy collaboration stack:

```bash
ansible-playbook -i inventory.yml 04-deploy-collaboration.yml
```

**What this deploys:**
- Outline (wiki)
- Wiki.js (technical docs)
- eLabFTW (lab notebook)
- Label Studio (data labeling)
- Nextcloud (file sync)
- Gitea (Git server)
- Kanboard (project management)
- Mattermost (team chat)
- Cal.com (scheduling)
- Jitsi Meet (video calls)

**Post-deployment:**
1. Configure Authentik SSO for all services
2. Create teams/organizations in each service
3. Setup Nextcloud external storage (MinIO)
4. Configure Mattermost → n8n webhooks

**Expected runtime:** 30-40 minutes

---

### Phase 5: Data & Analytics (Optional)

Deploy analytics stack:

```bash
ansible-playbook -i inventory.yml 05-deploy-analytics.yml
```

**What this deploys:**
- Metabase (BI dashboards)
- Apache Superset (advanced analytics)
- Prefect (workflow orchestration)
- Redash (SQL dashboards)

**Expected runtime:** 15-20 minutes

---

### Phase 6: User Services (Week 2, Day 2)

Deploy per-user services:

```bash
# Deploy for all users
ansible-playbook -i inventory.yml 06-deploy-user-services.yml

# Or deploy for specific user
ansible-playbook -i inventory.yml 06-deploy-user-services.yml --limit user1-services
```

**What this deploys per user:**
- Open WebUI (chat interface)
- n8n (workflow automation)
- Flowise (low-code AI)
- JupyterHub (notebooks) - optional
- RStudio Server (R IDE) - optional

**Post-deployment:**
1. Verify Open WebUI connects to Ollama (10.0.6.10:11434)
2. Test RAG with Qdrant connection
3. Create n8n workflows with Ollama integration
4. Setup Langfuse tracing for each user

**Expected runtime:** 10-15 minutes per user

---

### Phase 7: Traefik Configuration (Week 2, Day 3)

Configure Traefik routing:

```bash
ansible-playbook -i inventory.yml 99-configure-traefik.yml
```

**What this configures:**
- Traefik routes for all services
- SSL certificates via Let's Encrypt
- Domain mapping for test-*.valuechainhackers.xyz
- Middlewares (auth, rate limiting, headers)

**Post-deployment:**
1. Verify all services accessible via HTTPS
2. Test SSO login flow via Authentik
3. Verify SSL certificates

**Expected runtime:** 10-15 minutes

---

## Service Integration Examples

### Open WebUI Configuration

Environment variables set by playbook:
```bash
OLLAMA_BASE_URL=http://10.0.6.10:11434
VECTOR_DB=qdrant
QDRANT_URI=http://10.0.6.10:6333
QDRANT_COLLECTION=user1_documents
LANGFUSE_PUBLIC_KEY=<from_vaultwarden>
LANGFUSE_SECRET_KEY=<from_vaultwarden>
LANGFUSE_HOST=http://10.0.6.10:3002
OAUTH_CLIENT_ID=<authentik_client>
OAUTH_CLIENT_SECRET=<from_vaultwarden>
```

### n8n Configuration

Environment variables:
```bash
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=10.0.6.10
DB_POSTGRESDB_DATABASE=user1_n8n
DB_POSTGRESDB_USER=postgres
DB_POSTGRESDB_PASSWORD=<from_vaultwarden>
NODE_FUNCTION_ALLOW_EXTERNAL=*
N8N_ENCRYPTION_KEY=<generated_per_user>
```

### Flowise Configuration

Environment variables:
```bash
FLOWISE_DATABASE_TYPE=postgres
FLOWISE_DATABASE_HOST=10.0.6.10
FLOWISE_DATABASE_NAME=user1_flowise
FLOWISE_DATABASE_USER=postgres
FLOWISE_DATABASE_PASSWORD=<from_vaultwarden>
```

---

## Secrets Management

### Initial Secrets Generation

All playbooks generate secrets automatically using Python's `secrets` module:
- 256-bit keys for encryption
- URL-safe tokens for passwords
- Unique per service and per user

### Secrets Storage

1. Generated secrets are saved to local files:
   - `critical-infrastructure-secrets-<timestamp>.txt`
   - `shared-ai-secrets-<timestamp>.txt`
   - `user1-secrets-<timestamp>.txt`

2. Manually import secrets to Vaultwarden:
   - Organization: AI Stack Infrastructure
   - Collections: Critical, Shared AI, User Services
   - Items: One per service with all credentials

3. Future deployments retrieve from Vaultwarden via API

---

## Adding New Users

To add a new user (e.g., User 4):

1. Update `inventory.yml`:
```yaml
user4-services:
  ansible_host: 10.0.6.14
  ansible_user: root
  ansible_python_interpreter: /usr/bin/python3
  container_name: user4-services
  user_id: user4
  user_name: "User 4"
  user_email: "user4@valuechainhackers.xyz"
  # ... ports and domain prefixes
```

2. Create LXC container in Proxmox:
```bash
pct create 614 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname user4-services \
  --cores 2 --memory 4096 --swap 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.14/24,gw=10.0.5.1 \
  --features nesting=1 \
  --unprivileged 1
pct start 614
```

3. Deploy services:
```bash
ansible-playbook -i inventory.yml 06-deploy-user-services.yml --limit user4-services
```

4. Update Traefik routing:
```bash
ansible-playbook -i inventory.yml 99-configure-traefik.yml --limit traefik_servers
```

---

## Troubleshooting

### Container Status Check
```bash
# Check all services on a host
ansible -i inventory.yml shared_ai_infrastructure -m shell -a "docker ps"

# Check specific service
ansible -i inventory.yml shared_ai_infrastructure -m shell -a "docker logs ollama"
```

### Service Health
```bash
# Open WebUI health
curl http://10.0.6.11:3000/health

# Ollama health
curl http://10.0.6.10:11434/api/tags

# Qdrant health
curl http://10.0.6.10:6333/collections
```

### Common Issues

**Issue**: Supabase containers fail to start with sysctl error
**Solution**: This is a known issue. The shared AI playbook will deploy Supabase without problematic containers or use alternative configurations.

**Issue**: Out of memory errors
**Solution**: Increase LXC container memory allocation in Proxmox

**Issue**: Ollama model not found
**Solution**: Pull models after deployment:
```bash
docker exec ollama ollama pull nomic-embed-text
docker exec ollama ollama pull llama3.2
```

---

## Maintenance

### Backup Strategy
```bash
# Backup all Docker volumes
ansible-playbook -i inventory.yml backup-volumes.yml

# Backup PostgreSQL databases
ansible-playbook -i inventory.yml backup-databases.yml
```

### Updates
```bash
# Update all containers (Watchtower does this automatically)
# Or manually:
ansible-playbook -i inventory.yml update-services.yml
```

### Monitoring
- Grafana: http://10.0.6.15:3100
- Uptime Kuma: http://10.0.6.15:3201
- Portainer: http://10.0.6.15:9443

---

## Resource Summary

**Total Infrastructure (3 users):**
- Containers: 8
- Total RAM: 62GB
- Total CPU: 26 cores
- Total Storage: 380GB
- Services: 50+

**Per Additional User:**
- RAM: +4GB
- CPU: +2 cores
- Storage: +20GB
- Services: +3-5

---

## Support & Documentation

- Architecture: `ARCHITECTURE-TEST.md`
- Service Analysis: `SERVICE-CATEGORIZATION.md`
- Main Project: `/home/chris/Documents/github/InstallLocalAiPackage/`

---

**Last Updated:** 2025-11-24
**Version:** 1.0
**Status:** Ready for Deployment
