# START HERE - Minimal AI Stack Deployment

## What You're About to Deploy

A minimal, working AI stack with:
- **Ollama** (LLM inference) - shared
- **Qdrant** (vector database) - shared
- **PostgreSQL** (database) - shared
- **Open WebUI** (ChatGPT-like interface) - per user
- **n8n** (workflow automation) - per user

**Total: 2 containers, ~14GB RAM, ready in ~1 hour**

---

## Step-by-Step Deployment

### Step 1: Setup Your Control Node (5 minutes)

**Option A: Use your current machine** (easiest)
```bash
cd /home/chris/Documents/github/InstallLocalAiPackage/ansible
./setup-control-node.sh
```

**Option B: Create dedicated orchestration container**
```bash
# On Proxmox host
pct create 600 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname ansible-control \
  --cores 1 --memory 1024 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.2/24,gw=10.0.5.1 \
  --unprivileged 1 \
  --rootfs local-lvm:10

pct start 600
pct enter 600

# Inside container
apt-get update && apt-get install -y ansible python3-pip sshpass git
ansible-galaxy collection install community.docker community.general
pip3 install docker docker-compose
```

---

### Step 2: Create LXC Containers in Proxmox (5 minutes)

```bash
# SSH to Proxmox host
ssh root@<proxmox-ip>

# Create Shared AI Infrastructure (10.0.6.10)
pct create 610 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname shared-ai-01 \
  --cores 8 --memory 20480 --swap 4096 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.10/24,gw=10.0.5.1 \
  --features nesting=1,keyctl=1 \
  --unprivileged 1 \
  --storage local-lvm --rootfs local-lvm:100

# Create User 1 Services (10.0.6.11)
pct create 611 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname user1-services \
  --cores 2 --memory 4096 --swap 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=10.0.6.11/24,gw=10.0.5.1 \
  --features nesting=1 \
  --unprivileged 1 \
  --storage local-lvm --rootfs local-lvm:20

# Start both containers
pct start 610
pct start 611

# Set root passwords
pct exec 610 -- passwd
pct exec 611 -- passwd
```

---

### Step 3: Setup SSH Access (2 minutes)

From your control node:

```bash
# Copy SSH key to containers
ssh-copy-id root@10.0.6.10
ssh-copy-id root@10.0.6.11

# Test connectivity
ssh root@10.0.6.10 "echo 'Connected to shared AI'"
ssh root@10.0.6.11 "echo 'Connected to user 1'"
```

---

### Step 4: Test Ansible Connectivity (1 minute)

```bash
cd /home/chris/Documents/github/InstallLocalAiPackage/ansible

# Test ping
ansible -i inventory-minimal.yml all -m ping

# Expected output:
# shared-ai-01 | SUCCESS => ...
# user1-services | SUCCESS => ...
```

If this fails, check SSH access and inventory file.

---

### Step 5: Deploy Shared AI Infrastructure (30 minutes)

```bash
ansible-playbook -i inventory-minimal.yml 02-deploy-shared-ai-minimal.yml
```

**What happens:**
1. Installs Docker on 10.0.6.10
2. Deploys PostgreSQL, Ollama, Qdrant
3. Pulls `nomic-embed-text` model (~300MB)
4. Creates databases for user1
5. Saves connection info to `./shared-ai-secrets-*.txt`

**Expected output:**
```
PLAY RECAP *****************************************************
shared-ai-01    : ok=30   changed=15   unreachable=0    failed=0
```

**Verify:**
```bash
# Check services are running
ssh root@10.0.6.10 "docker ps"

# Should see: shared-postgres, ollama, qdrant

# Test Ollama
curl http://10.0.6.10:11434/api/tags
```

---

### Step 6: Deploy User Services (15 minutes)

**IMPORTANT:** First, get the PostgreSQL password from `shared-ai-secrets-*.txt`

```bash
# Look for this file
ls -lt ./shared-ai-secrets-*.txt | head -1

# Note the POSTGRES_PASSWORD value
cat <filename>
```

Now deploy:

```bash
ansible-playbook -i inventory-minimal.yml 06-deploy-user-services-minimal.yml
```

**What happens:**
1. Installs Docker on 10.0.6.11
2. Deploys Open WebUI and n8n
3. Saves secrets to `./user1-secrets-*.txt`
4. **Shows warning about updating PostgreSQL password**

**Fix the password:**
```bash
# SSH to user container
ssh root@10.0.6.11

# Edit .env file
nano /opt/user1-services/.env

# Replace CHANGEME with actual POSTGRES_PASSWORD

# Restart services
cd /opt/user1-services
docker compose restart
```

**Verify:**
```bash
# Check services
ssh root@10.0.6.11 "docker ps"

# Should see: user1-openwebui, user1-n8n

# Test Open WebUI
curl http://10.0.6.11:3000

# Test n8n
curl http://10.0.6.11:5678
```

---

### Step 7: Access & Test (10 minutes)

#### Open WebUI
1. Open browser: http://10.0.6.11:3000
2. Click "Sign up" and create account
3. Once logged in, chat should load
4. Select model (nomic-embed-text should be available)
5. Send a test message
6. ✅ You should get a response from Ollama

#### n8n
1. Open browser: http://10.0.6.11:5678
2. Complete setup wizard (create admin account)
3. Create new workflow
4. Add "HTTP Request" node:
   - Method: POST
   - URL: http://10.0.6.10:11434/api/generate
   - Body:
     ```json
     {
       "model": "nomic-embed-text",
       "prompt": "Hello from n8n!",
       "stream": false
     }
     ```
5. Execute workflow
6. ✅ Should receive response from Ollama

---

## What You Have Now

### Services Running

**Container 10.0.6.10 (Shared AI):**
- PostgreSQL (port 5432)
- Ollama (port 11434)
- Qdrant (port 6333)

**Container 10.0.6.11 (User 1):**
- Open WebUI (port 3000) → connects to Ollama & Qdrant
- n8n (port 5678) → connects to PostgreSQL & Ollama

### Resource Usage
- **Shared AI**: ~10-12GB RAM actual usage
- **User 1**: ~1-2GB RAM actual usage
- **Total**: ~12-14GB RAM

---

## What's Next?

### Immediate Next Steps
1. **Pull more models:**
   ```bash
   ssh root@10.0.6.10
   docker exec ollama ollama pull llama3.2
   docker exec ollama ollama pull mistral
   ```

2. **Test RAG in Open WebUI:**
   - Upload a document
   - Ask questions about it
   - Should use Qdrant for vector search

3. **Create n8n automation:**
   - Build workflow that calls Ollama
   - Process results
   - Store in PostgreSQL

### Future Enhancements

**Add Traefik (SSL/domains):**
- Deploy Phase 7 playbook
- Access via https://test-openwebui.valuechainhackers.xyz

**Add Authentication (SSO):**
- Deploy Phase 1 (Authentik, Vaultwarden)
- Configure OAuth2 for all services

**Add Monitoring:**
- Deploy Phase 3 (Grafana, Prometheus)
- Track resource usage and performance

**Add More Users:**
- Create container 10.0.6.12
- Run playbook with `--limit user2-services`
- Each user gets isolated Open WebUI + n8n

**Full Stack:**
- Deploy all phases from [README.md](README.md)
- 50+ services across 8 containers
- Complete research lab infrastructure

---

## Troubleshooting

### Ansible fails with "command not found"
```bash
# Install Ansible collections
ansible-galaxy collection install community.docker community.general
```

### Container won't start
```bash
# Check container status
pct status 610

# Check journalctl
pct enter 610
journalctl -xe
```

### Docker fails to install
```bash
# Verify LXC features
pct config 610 | grep features
# Should show: nesting=1,keyctl=1

# If not, update:
pct set 610 -features nesting=1,keyctl=1
pct reboot 610
```

### Open WebUI can't connect to Ollama
```bash
# Check Ollama is running
ssh root@10.0.6.10 "docker logs ollama"

# Test from user container
ssh root@10.0.6.11 "curl http://10.0.6.10:11434/api/tags"
```

### n8n database connection fails
```bash
# Verify PostgreSQL password in .env
ssh root@10.0.6.11 "cat /opt/user1-services/.env | grep POSTGRES"

# Test PostgreSQL connection
ssh root@10.0.6.11 "docker exec user1-n8n nc -zv 10.0.6.10 5432"

# Check PostgreSQL logs
ssh root@10.0.6.10 "docker logs shared-postgres"
```

---

## Support

- **Quick Start Guide:** [QUICK-START.md](QUICK-START.md)
- **Full Documentation:** [README.md](README.md)
- **Validation Results:** [VALIDATION-RESULTS.md](VALIDATION-RESULTS.md)
- **Architecture:** [ARCHITECTURE-TEST.md](ARCHITECTURE-TEST.md)

---

## Estimated Timeline

| Step | Time | Notes |
|------|------|-------|
| 1. Setup Control Node | 5 min | One-time setup |
| 2. Create Containers | 5 min | In Proxmox |
| 3. SSH Setup | 2 min | ssh-copy-id |
| 4. Test Ansible | 1 min | ansible ping |
| 5. Deploy Shared AI | 30 min | Includes model download |
| 6. Deploy User Services | 15 min | Includes password fix |
| 7. Test Services | 10 min | Open WebUI + n8n |
| **Total** | **~1 hour** | First-time deployment |

**Subsequent user deployments: ~15 minutes each**

---

**Ready?** Start with [Step 1: Setup Control Node](#step-1-setup-your-control-node-5-minutes)
