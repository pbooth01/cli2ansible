# CLI2Ansible Demo Guide

This guide walks you through a complete demo of converting terminal commands into an Ansible role.

## Prerequisites

1. **Start the services:**
   ```bash
   # Make sure Docker is running
   make docker-up
   
   # Or if using Poetry directly:
   poetry run uvicorn cli2ansible.app:app --reload
   ```

2. **Verify services are running:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001 (login: minioadmin/minioadmin)

## Demo Scenario: Setting up Nginx

Let's convert a manual nginx setup workflow into an Ansible role.

### Step 1: Create a Session

```bash
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "nginx-setup-demo",
    "metadata": {
      "description": "Demo: Setting up Nginx web server",
      "environment": "production"
    }
  }')

# Extract session ID
SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.id')
echo "Created session: $SESSION_ID"
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "nginx-setup-demo",
  "status": "created",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "metadata": {...}
}
```

### Step 2: Upload Terminal Events

Simulate terminal commands by uploading events. Each event represents output from a terminal session.

```bash
curl -X POST "http://localhost:8000/sessions/$SESSION_ID/events" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "timestamp": 1.0,
      "event_type": "o",
      "data": "sudo apt-get update\n",
      "sequence": 0
    },
    {
      "timestamp": 2.0,
      "event_type": "o",
      "data": "sudo apt-get install -y nginx\n",
      "sequence": 1
    },
    {
      "timestamp": 3.0,
      "event_type": "o",
      "data": "sudo systemctl start nginx\n",
      "sequence": 2
    },
    {
      "timestamp": 4.0,
      "event_type": "o",
      "data": "sudo systemctl enable nginx\n",
      "sequence": 3
    }
  ]'
```

**Expected Response:**
```json
{
  "status": "uploaded",
  "count": "4"
}
```

### Step 3: Compile Session to Ansible Role

This extracts commands from events and translates them to Ansible tasks:

```bash
curl -X POST "http://localhost:8000/sessions/$SESSION_ID/compile" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "artifact_url": "sessions/{session_id}/role.zip",
  "download_url": "http://localhost:9000/cli2ansible-artifacts/sessions/..."
}
```

### Step 4: View Translation Report

See what was translated and with what confidence:

```bash
curl "http://localhost:8000/sessions/$SESSION_ID/report"
```

**Expected Response:**
```json
{
  "session_id": "...",
  "total_commands": 4,
  "high_confidence": 3,
  "medium_confidence": 0,
  "low_confidence": 1,
  "warnings": [],
  "skipped_commands": [],
  "generated_at": "2024-01-15T10:35:00"
}
```

### Step 5: Download the Generated Role

```bash
curl "http://localhost:8000/sessions/$SESSION_ID/playbook" \
  -o nginx-role.zip

# Extract and examine
unzip nginx-role.zip -d nginx-role
cd nginx-role/nginx-setup-demo
tree
```

**Generated Structure:**
```
nginx-setup-demo/
├── tasks/
│   └── main.yml          # Ansible tasks
├── handlers/
│   └── main.yml          # Handlers (if any)
├── vars/
│   └── main.yml          # Variables
├── defaults/
│   └── main.yml          # Default variables
├── meta/
│   └── main.yml          # Role metadata
├── molecule/
│   └── default/          # Molecule test config
├── README.md             # Generated documentation
```

### Step 6: View Generated Tasks

```bash
cat tasks/main.yml
```

**Example Output:**
```yaml
---
- name: Update apt cache
  apt:
    update_cache: true
    cache_valid_time: 3600
  become: true

- name: Install packages: nginx
  apt:
    name:
      - nginx
    state: present
    update_cache: true
  become: true

- name: Start service: nginx
  systemd:
    name: nginx
    state: started
  become: true

- name: Enable service: nginx
  systemd:
    name: nginx
    enabled: true
  become: true
```

## Quick Demo Script

Save this as `demo.sh`:

```bash
#!/bin/bash
set -e

API_URL="http://localhost:8000"

echo "🚀 CLI2Ansible Demo"
echo "=================="

# Step 1: Create session
echo -e "\n1️⃣ Creating session..."
SESSION_RESPONSE=$(curl -s -X POST "$API_URL/sessions" \
  -H "Content-Type: application/json" \
  -d '{"name": "demo-nginx", "metadata": {}}')
SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.id')
echo "   ✅ Session created: $SESSION_ID"

# Step 2: Upload events
echo -e "\n2️⃣ Uploading terminal events..."
curl -s -X POST "$API_URL/sessions/$SESSION_ID/events" \
  -H "Content-Type: application/json" \
  -d '[
    {"timestamp": 1.0, "event_type": "o", "data": "sudo apt-get update\n", "sequence": 0},
    {"timestamp": 2.0, "event_type": "o", "data": "sudo apt-get install -y nginx\n", "sequence": 1},
    {"timestamp": 3.0, "event_type": "o", "data": "sudo systemctl start nginx\n", "sequence": 2},
    {"timestamp": 4.0, "event_type": "o", "data": "sudo systemctl enable nginx\n", "sequence": 3}
  ]' > /dev/null
echo "   ✅ Events uploaded"

# Step 3: Compile
echo -e "\n3️⃣ Compiling to Ansible role..."
curl -s -X POST "$API_URL/sessions/$SESSION_ID/compile" \
  -H "Content-Type: application/json" \
  -d '{}' > /dev/null
echo "   ✅ Compilation complete"

# Step 4: Get report
echo -e "\n4️⃣ Translation Report:"
curl -s "$API_URL/sessions/$SESSION_ID/report" | jq '{
  total_commands,
  high_confidence,
  medium_confidence,
  low_confidence
}'

# Step 5: Download
echo -e "\n5️⃣ Downloading role..."
curl -s "$API_URL/sessions/$SESSION_ID/playbook" -o demo-role.zip
echo "   ✅ Downloaded to demo-role.zip"

echo -e "\n✨ Demo complete! Extract demo-role.zip to see the generated Ansible role."
```

Make it executable and run:
```bash
chmod +x demo.sh
./demo.sh
```

## Interactive Demo with API Docs

For a visual demo, use the FastAPI interactive docs:

1. Open http://localhost:8000/docs
2. Try each endpoint:
   - `POST /sessions` - Create a session
   - `POST /sessions/{id}/events` - Upload events
   - `POST /sessions/{id}/compile` - Compile to Ansible
   - `GET /sessions/{id}/report` - View translation report
   - `GET /sessions/{id}/playbook` - Download role

## Advanced Demo Scenarios

### Multi-step Workflow

```bash
# Install multiple packages + configure service
curl -X POST "$API_URL/sessions/$SESSION_ID/events" \
  -H "Content-Type: application/json" \
  -d '[
    {"timestamp": 1.0, "event_type": "o", "data": "sudo apt-get install -y nginx postgresql redis\n", "sequence": 0},
    {"timestamp": 2.0, "event_type": "o", "data": "sudo mkdir -p /var/www/html\n", "sequence": 1},
    {"timestamp": 3.0, "event_type": "o", "data": "sudo systemctl enable nginx postgresql redis\n", "sequence": 2}
  ]'
```

### Git Clone Workflow

```bash
curl -X POST "$API_URL/sessions/$SESSION_ID/events" \
  -H "Content-Type: application/json" \
  -d '[
    {"timestamp": 1.0, "event_type": "o", "data": "git clone https://github.com/user/repo.git /opt/app\n", "sequence": 0},
    {"timestamp": 2.0, "event_type": "o", "data": "cd /opt/app && pip install -r requirements.txt\n", "sequence": 1}
  ]'
```

## Troubleshooting

### Services not starting?
```bash
# Check Docker status
docker-compose ps

# View logs
make docker-logs
# or
docker-compose logs -f
```

### API not responding?
```bash
# Check if API is running
curl http://localhost:8000/

# Should return: {"status":"ok","service":"cli2ansible"}
```

### Database connection issues?
```bash
# Ensure PostgreSQL is healthy
docker-compose ps postgres

# Check database URL in settings
# Default: postgresql+psycopg://postgres:postgres@localhost:5432/cli2ansible
```

## Next Steps

- Review the generated Ansible role structure
- Test the role with Molecule (if installed)
- Customize the translation rules in `src/cli2ansible/adapters/outbound/translator/rules_engine.py`
- Add more command patterns to support additional workflows

