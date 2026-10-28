#!/usr/bin/env bash
# ==============================================================================
# CodeWithAnil — Automated Oracle Cloud Ampere A1 (ARM64) Provisioning Script
# Target OS: Ubuntu 22.04 LTS / 24.04 LTS (aarch64)
# ==============================================================================

set -euo pipefail

# Ensure script is executed as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Please run this setup script with sudo: sudo ./setup.sh"
    exit 1
fi

REPO_URL="https://github.com/anilyadav7488/codewithanil.git"
APP_DIR="/opt/codewithanil"
BACKEND_DIR="${APP_DIR}/backend"
APP_USER="ubuntu"
DB_NAME="codewithanil"
DB_USER="codewithanil_user"

echo "=================================================================="
echo " Starting CodeWithAnil Production Setup for Oracle Cloud ARM64    "
echo "=================================================================="

# 1. Update OS and install foundational dependencies
echo "[1/9] Updating system packages and installing dependencies..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    ufw \
    fail2ban \
    curl \
    iptables-persistent

# 2. Fix Oracle Cloud default iptables rules (Oracle drops incoming 80/443 by default)
echo "[2/9] Configuring Oracle Cloud network packet filtering..."
iptables -I INPUT 6 -p tcp --dport 80 -j ACCEPT || true
iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT || true
netfilter-persistent save || true

# Configure UFW
ufw allow 22/tcp || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true
ufw --force enable || true

# 3. Configure local PostgreSQL
echo "[3/9] Provisioning local PostgreSQL database..."
systemctl start postgresql
systemctl enable postgresql

DB_PASS=$(openssl rand -hex 16)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"

# 4. Clone or pull application code
echo "[4/9] Syncing CodeWithAnil repository to ${APP_DIR}..."
if [ ! -d "${APP_DIR}" ]; then
    git clone "${REPO_URL}" "${APP_DIR}"
else
    cd "${APP_DIR}"
    git pull origin main || true
fi

chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

# 5. Set up Python virtual environment on ARM64
echo "[5/9] Initializing Python virtual environment on ARM64..."
cd "${BACKEND_DIR}"
if [ ! -d ".venv" ]; then
    sudo -u "${APP_USER}" python3 -m venv .venv
fi

# Upgrade pip and install CPU-only PyTorch & dependencies from PyPI manylinux_aarch64 wheels
echo "[6/9] Installing dependencies (PyTorch CPU, Transformers, FastAPI)..."
sudo -u "${APP_USER}" .venv/bin/pip install --upgrade pip setuptools wheel
sudo -u "${APP_USER}" .venv/bin/pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
sudo -u "${APP_USER}" .venv/bin/pip install --no-cache-dir -r requirements.txt

# 6. Generate production .env file
echo "[7/9] Writing production environment file..."
JWT_SECRET=$(openssl rand -hex 32)
ENV_FILE="${BACKEND_DIR}/.env"

if [ ! -f "${ENV_FILE}" ]; then
    cat <<EOF > "${ENV_FILE}"
PROJECT_NAME=CodeWithAnil
ENVIRONMENT=production
API_V1_STR=/api
SECRET_KEY=${JWT_SECRET}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@127.0.0.1:5432/${DB_NAME}
CORS_ORIGINS=["https://codewithanil.vercel.app"]
HF_MODEL_NAME=Hello-SimpleAI/chatgpt-detector-roberta
INFERENCE_DEVICE=cpu
MAX_SEQUENCE_LENGTH=512
INCONCLUSIVE_LOWER_THRESHOLD=0.40
INCONCLUSIVE_UPPER_THRESHOLD=0.60
RATE_LIMIT_PER_MINUTE=60
MAX_UPLOAD_SIZE_MB=15
EOF
    chown "${APP_USER}:${APP_USER}" "${ENV_FILE}"
    chmod 600 "${ENV_FILE}"
    echo "Generated new production .env configuration."
else
    echo "Preserved existing .env file."
fi

# 7. Preload the Hugging Face model and run Alembic database migrations
echo "[8/9] Preloading RoBERTa model into disk cache & running migrations..."
sudo -u "${APP_USER}" .venv/bin/python3 -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; m = 'Hello-SimpleAI/chatgpt-detector-roberta'; AutoTokenizer.from_pretrained(m); AutoModelForSequenceClassification.from_pretrained(m)"
sudo -u "${APP_USER}" .venv/bin/alembic upgrade head

# 8. Install and start systemd service
echo "[9/9] Configuring and starting Systemd service & Nginx..."
cp "${APP_DIR}/deployment/oracle-arm64/codewithanil.service" /etc/systemd/system/codewithanil.service
systemctl daemon-reload
systemctl enable codewithanil.service
systemctl restart codewithanil.service

# Configure Nginx
cp "${APP_DIR}/deployment/oracle-arm64/nginx.conf" /etc/nginx/sites-available/codewithanil
ln -sf /etc/nginx/sites-available/codewithanil /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default || true
nginx -t
systemctl reload nginx

echo ""
echo "=================================================================="
echo " CodeWithAnil Backend is Successfully Deployed on ARM64!          "
echo "=================================================================="
echo " Local Health Probe: curl http://127.0.0.1:8000/api/health        "
echo " Systemd Service   : sudo systemctl status codewithanil           "
echo " Live Logs         : sudo journalctl -u codewithanil -f           "
echo " Next Step (SSL)   : sudo certbot --nginx -d api.yourdomain.com   "
echo "=================================================================="
