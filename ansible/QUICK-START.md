# Quick Start - Minimal AI Stack Deployment

## Goal
Deploy the absolute minimum viable AI stack to test the concept:
- 1 container with Ollama + Qdrant + PostgreSQL (shared)
- 1 container with Open WebUI + n8n (user services)
- Traefik routing (already exists at 10.0.4.10)

**No SSO, no monitoring, no extras - just the core AI functionality.**

---

## Architecture (Minimal)

```
10.0.4.10  - Traefik (already running)
10.0.6.10  - Shared AI (Ollama, Qdrant, PostgreSQL)
10.0.6.11  - User 1 (Open WebUI, n8n)
```

---

## Prerequisites

### 1. Ansible Control Node

**Option A: Use your current machine**
```bash
sudo apt-get update && sudo apt-get install -y ansible python3-pip sshpass
ansible-galaxy collection install community.docker community.general
pip3 install --user docker docker-compose
```

**Option B: Create dedicated orchestration container**
```bash
# On Proxmox host
pct create 600 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname ansible-control \
  --cores 1 --memory 1024 --swap 512 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.2/24,gw=10.0.5.1 \
  --unprivileged 1 \
  --storage local-lvm --rootfs local-lvm:10

pct start 600

# Inside container
apt-get update && apt-get install -y ansible python3-pip sshpass git
ansible-galaxy collection install community.docker community.general
pip3 install docker docker-compose
```

### 2. Create LXC Containers in Proxmox

```bash
# Shared AI Infrastructure (10.0.6.10)
pct create 610 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname shared-ai-01 \
  --cores 8 --memory 20480 --swap 4096 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.10/24,gw=10.0.5.1 \
  --features nesting=1,keyctl=1 \
  --unprivileged 1 \
  --storage local-lvm --rootfs local-lvm:100

# User 1 Services (10.0.6.11)
pct create 611 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname user1-services \
  --cores 2 --memory 4096 --swap 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.11/24,gw=10.0.5.1 \
  --features nesting=1 \
  --unprivileged 1 \
  --storage local-lvm --rootfs local-lvm:20

# Start containers
pct start 610
pct start 611
```

### 3. Setup SSH Access

```bash
# Set root passwords on containers
pct exec 610 -- passwd
pct exec 611 -- passwd

# Or copy SSH key
ssh-copy-id root@10.0.6.10
ssh-copy-id root@10.0.6.11
```

---

## Deployment

### Step 1: Clone this repository
```bash
git clone <your-repo>
cd InstallLocalAiPackage/ansible
```

### Step 2: Create minimal inventory

Create `inventory-minimal.yml`:
```yaml
all:
  children:
    shared_ai:
      hosts:
        shared-ai-01:
          ansible_host: 10.0.6.10
          ansible_user: root
          ansible_python_interpreter: /usr/bin/python3

    user_services:
      hosts:
        user1-services:
          ansible_host: 10.0.6.11
          ansible_user: root
          ansible_python_interpreter: /usr/bin/python3
          user_id: user1

  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
    base_domain: valuechainhackers.xyz
```

### Step 3: Deploy Shared AI Infrastructure

```bash
ansible-playbook -i inventory-minimal.yml 02-deploy-shared-ai-minimal.yml
```

**What this deploys:**
- Ollama (LLM inference)
- Qdrant (vector database)
- PostgreSQL (database)

**Time:** ~20-30 minutes (including Ollama model download)

### Step 4: Deploy User Services

```bash
ansible-playbook -i inventory-minimal.yml 06-deploy-user-services-minimal.yml
```

**What this deploys:**
- Open WebUI (connected to Ollama, Qdrant)
- n8n (connected to PostgreSQL, Ollama)

**Time:** ~10-15 minutes

### Step 5: Configure Traefik (Optional)

```bash
ansible-playbook -i inventory-minimal.yml 99-configure-traefik-minimal.yml
```

---

## Testing

### Access Services

**Via IP (immediate):**
- Open WebUI: http://10.0.6.11:3000
- n8n: http://10.0.6.11:5678
- Ollama API: http://10.0.6.10:11434

**Via Domain (after Traefik config):**
- Open WebUI: https://test-openwebui.valuechainhackers.xyz
- n8n: https://test-n8n.valuechainhackers.xyz

### Test Ollama

```bash
# Pull a model
ssh root@10.0.6.10 "docker exec ollama ollama pull nomic-embed-text"
ssh root@10.0.6.10 "docker exec ollama ollama pull llama3.2"

# Test inference
curl http://10.0.6.10:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

### Test Open WebUI → Ollama

1. Access http://10.0.6.11:3000
2. Create account
3. Select model (llama3.2)
4. Send message
5. ✅ Should get response from Ollama

### Test n8n → Ollama

1. Access http://10.0.6.11:5678
2. Setup admin account
3. Create workflow with HTTP Request node
4. Configure: POST http://10.0.6.10:11434/api/generate
5. ✅ Should get LLM response

---

## What's Next?

Once this minimal stack is working:

1. **Add Authentication** - Deploy Phase 1 (Authentik, Vaultwarden)
2. **Add Monitoring** - Deploy Phase 3 (Grafana, Prometheus)
3. **Add Collaboration** - Deploy Phase 4 (Mattermost, Gitea, etc.)
4. **Scale Users** - Deploy more user containers (10.0.6.12, 10.0.6.13)

---

## Troubleshooting

### Container won't start
```bash
# Check status
pct status 610

# View logs
pct enter 610
journalctl -xe
```

### Ansible connection fails
```bash
# Test SSH
ssh root@10.0.6.10

# Test Ansible ping
ansible -i inventory-minimal.yml all -m ping
```

### Docker service not starting
```bash
ssh root@10.0.6.10
systemctl status docker
systemctl start docker
```

### Ollama not responding
```bash
ssh root@10.0.6.10
docker logs ollama
docker restart ollama
```

---

## Resource Usage (Minimal Setup)

**Container 10.0.6.10 (Shared AI):**
- RAM: ~10-12GB actual usage
- CPU: 4-6 cores during inference
- Storage: ~30GB (models + data)

**Container 10.0.6.11 (User 1):**
- RAM: ~1-2GB actual usage
- CPU: 1 core
- Storage: ~5GB

**Total: ~12-14GB RAM, suitable for a server with 32GB+**

---

**Next:** [Full Deployment Guide](README.md) for complete infrastructure
