# CodeWithAnil — Zero-Cost Production Deployment Guide (Oracle Cloud ARM64 + Vercel)

**Target Architecture:**
- **Frontend:** Vercel Hobby (Free Global CDN / Edge Network)
- **Backend:** Oracle Cloud Always Free Ampere A1 Compute (ARM64, Ubuntu 22.04/24.04 LTS)
- **Database:** Local PostgreSQL on the same Oracle Cloud VM (High-speed Unix socket, zero latency, zero extra cost)
- **Model:** `Hello-SimpleAI/chatgpt-detector-roberta` (100% real transformer inference, cached on NVMe)
- **Total Monthly Cost:** **$0.00 / month forever**

---

## 1. ARM64 (aarch64) Compatibility Audit Report

Prior to preparing this setup, a full automated compatibility audit of all backend Python wheels was conducted against PyPI's official repository for Linux ARM64 (`manylinux_aarch64`).

### Audit Findings
| Package | Latest Wheel Type | ARM64 Compatible? | Operational Assessment |
|---|---|:---:|---|
| **PyTorch (`torch`)** | `manylinux_2_28_aarch64` | **YES** | Prebuilt binary wheel available on standard PyPI & PyTorch CPU index. No compilation required. |
| **Transformers** | `py3-none-any.whl` | **YES** | Pure Python universal package. |
| **Tokenizers** | `abi3-manylinux_aarch64` | **YES** | Native Rust binary precompiled for ARM64. |
| **Safetensors** | `abi3-manylinux_aarch64` | **YES** | Native Rust binary precompiled for ARM64. |
| **NumPy & SciPy** | `manylinux_2_27_aarch64` | **YES** | Native C/Fortran SIMD-optimized binaries for Neoverse-N1. |
| **Scikit-Learn** | `manylinux_2_28_aarch64` | **YES** | Prebuilt native binary for aarch64. |
| **Pandas** | `manylinux_2_24_aarch64` | **YES** | Prebuilt native binary for aarch64. |
| **psycopg2-binary** | `manylinux2014_aarch64` | **YES** | Native PostgreSQL client library prebuilt for ARM64. |
| **Bcrypt** | `manylinux2014_aarch64` | **YES** | Native Rust/C password hashing prebuilt for ARM64. |
| **ReportLab & PyPDF** | `py3-none-any.whl` | **YES** | Pure Python document generation libraries. |
| **FastAPI & Uvicorn** | `py3-none-any.whl` | **YES** | Fully operational on Linux ARM64. |

> [!NOTE]
> **Audit Conclusion:** **Zero blockers.** Every dependency in CodeWithAnil supports native Linux ARM64 out-of-the-box without manual C/C++ compilation.

---

## 2. Why Oracle Cloud Ampere A1 (Zero Cost vs Render)

| Metric | Render Free Plan | Oracle Cloud Always Free Ampere A1 |
|---|---|---|
| **RAM Limit** | **512 MB** *(Crashes RoBERTa model with Out-Of-Memory)* | **6 GB to 24 GB** *(RoBERTa takes ~800 MB, leaving 95% RAM free)* |
| **CPU Power** | 0.1 CPU (shared, throttled) | **1 to 4 dedicated OCPU** (Ampere Altra 3.0 GHz) |
| **Storage** | Ephemeral (resets on restart) | **50 GB to 200 GB NVMe** (Persistent block volume) |
| **Sleep Inactivity** | Spins down after 15 minutes of idle | **Runs 24/7 continuously** without sleep or cold starts |
| **Monthly Cost** | Free (Unusable for RoBERTa) / $7/mo for Starter | **$0.00 / month forever** |

---

## 3. Step 1: Create Oracle Cloud Always Free Instance

1. Log in to your [Oracle Cloud Console](https://cloud.oracle.com).
2. Go to **Compute** -> **Instances** -> Click **Create Instance**.
3. Configure the VM:
   - **Name:** `codewithanil-backend`
   - **Placement:** Any Available Domain with *Always Free Eligible* badge.
   - **Image:** Click *Change Image* -> Choose **Canonical Ubuntu** -> Select **Ubuntu 22.04 LTS** or **Ubuntu 24.04 LTS** (Ensure Architecture is **Arm**).
   - **Shape:** Click *Change Shape* -> Select **Ampere** -> **VM.Standard.A1.Flex**:
     - **OCPU:** `2` (or up to `4`)
     - **Memory (RAM):** `12 GB` (or up to `24 GB`)
     *(Both are 100% Always Free)*
   - **Networking:** Select *Create new virtual cloud network* -> Ensure **Assign a public IPv4 address** is checked.
   - **SSH Keys:** Download your private key (`id_rsa`) or paste your existing public key.
   - **Boot Volume:** Default (50 GB or up to 200 GB Always Free).
4. Click **Create**. Within 60 seconds, your instance status will turn **Running** and display a **Public IP Address** (e.g. `140.238.xx.xx`).

---

## 4. Step 2: Open Ingress Ports in Oracle Cloud VCN

By default, Oracle Cloud's Virtual Cloud Network (VCN) blocks external web traffic. You must permit Ports 80 and 443:

1. In the instance details, click on your **Virtual Cloud Network** link (under *Primary VNIC*).
2. In the left navigation, click **Security Lists** -> Click **Default Security List for...**.
3. Click **Add Ingress Rules**:
   - **Source CIDR:** `0.0.0.0/0`
   - **IP Protocol:** `TCP`
   - **Destination Port Range:** `80,443`
   - **Description:** `Allow HTTP and HTTPS inbound`
4. Click **Add Ingress Rules**.

---

## 5. Step 3: Run the Automated Setup Script on the VM

Connect to your Oracle VM from your local Windows terminal:
```cmd
ssh -i "path\to\your-ssh-key.key" ubuntu@<YOUR_ORACLE_PUBLIC_IP>
```

Once connected, run these commands to execute the automated provisioning script:

```bash
# 1. Update git and clone repository
git clone https://github.com/anilyadav7488/codewithanil.git /opt/codewithanil

# 2. Navigate to deployment folder and make scripts executable
cd /opt/codewithanil/deployment/oracle-arm64
chmod +x setup.sh monitor.sh

# 3. Run the automated installer (installs PostgreSQL, Nginx, PyTorch ARM64, and Systemd)
sudo ./setup.sh
```

### What `setup.sh` automatically does:
- Updates apt and installs Python 3, Git, PostgreSQL, Nginx, Certbot, and firewall tools.
- Fixes the default Oracle Cloud OS `iptables` drop rules to unblock HTTP/HTTPS ports.
- Creates the local PostgreSQL database (`codewithanil`) and user (`codewithanil_user`) with a secure random password.
- Sets up an ARM64 Python virtual environment and installs prebuilt `manylinux_aarch64` PyTorch wheels.
- Pre-downloads the Hugging Face `Hello-SimpleAI/chatgpt-detector-roberta` model to disk cache.
- Runs database migrations via `alembic upgrade head`.
- Installs and enables `codewithanil.service` under systemd with auto-restart.
- Configures Nginx reverse proxy with `client_max_body_size 20M` and reloads Nginx.

---

## 6. Step 4: Configure Free HTTPS with Let's Encrypt

1. Point your domain or a free subdomain (e.g. from DuckDNS, Cloudflare, or your custom domain) to your Oracle VM Public IP:
   - **Type:** `A`
   - **Name:** `api` (e.g. `api.yourdomain.com`)
   - **Value:** `<YOUR_ORACLE_PUBLIC_IP>`

2. Update `/etc/nginx/sites-available/codewithanil` with your domain:
   ```bash
   sudo sed -i 's/api.yourdomain.com/api.yourdomain.com/g' /etc/nginx/sites-available/codewithanil
   sudo nginx -t && sudo systemctl reload nginx
   ```

3. Obtain an automated SSL certificate with auto-renewal:
   ```bash
   sudo certbot --nginx -d api.yourdomain.com
   ```
   Certbot will verify your domain, install the SSL certificate, and configure HTTPS automatically.

---

## 7. Step 5: Connect Vercel Frontend to the Oracle Backend

1. In your local repository, push the latest code:
   ```cmd
   git add .
   git commit -m "feat: configure zero-cost Oracle Cloud ARM64 deployment"
   git push origin main
   ```

2. Open the [Vercel Dashboard](https://vercel.com) -> Select your `codewithanil` project.
3. Go to **Settings** -> **Environment Variables**.
4. Add / Update:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://api.yourdomain.com/api` (or `http://<YOUR_ORACLE_PUBLIC_IP>/api` if testing without domain)
5. Click **Save** and trigger a **Redeploy** on Vercel.

6. On your Oracle VM, whitelist your Vercel URL in `/opt/codewithanil/backend/.env`:
   ```bash
   sudo nano /opt/codewithanil/backend/.env
   ```
   Ensure `CORS_ORIGINS` contains your Vercel URL:
   ```env
   CORS_ORIGINS=["https://codewithanil.vercel.app","https://codewithanil-anilyadav7488s-projects.vercel.app"]
   ```
   Restart the backend service:
   ```bash
   sudo systemctl restart codewithanil
   ```

---

## 8. Verification & Health Monitoring

### Check Service Health
Run the included monitoring tool on your Oracle VM:
```bash
/opt/codewithanil/deployment/oracle-arm64/monitor.sh
```

Example healthy output:
```
==================================================================
           CodeWithAnil Production Service Status Monitor         
==================================================================
[ OK ] Service 'codewithanil' is running.
[ OK ] Service 'nginx' is running.
[ OK ] Service 'postgresql' is running.

Probing internal API health endpoint (http://127.0.0.1:8000/api/health)...
[ OK ] FastAPI returned HTTP 200.
{"status":"healthy","service":"CodeWithAnil API","timestamp":"2026-10-28T12:00:00Z","model_loaded":true,"model_name":"Hello-SimpleAI/chatgpt-detector-roberta"}

Memory & CPU Consumption (FastAPI / Uvicorn):
  PID  PPID  %CPU %MEM   RSS CMD
 4210     1   0.2  6.5 812M /opt/codewithanil/backend/.venv/bin/python3 ... uvicorn

System Memory Overview:
               total        used        free      shared  buff/cache   available
Mem:            11Gi       1.2Gi       8.4Gi        48Mi       1.8Gi       9.9Gi

Disk Storage Overview:
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        46G  6.8G   39G  15% /
==================================================================
```

### View Live Logs
```bash
sudo journalctl -u codewithanil -f
```

### Useful Maintenance Commands
- Restart Backend: `sudo systemctl restart codewithanil`
- Reload Nginx: `sudo systemctl reload nginx`
- Restart Database: `sudo systemctl restart postgresql`
- Run Database Migrations: `cd /opt/codewithanil/backend && sudo -u ubuntu .venv/bin/alembic upgrade head`
