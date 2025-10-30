# Production Deployment Guide for Organization Private Server

This guide will help you securely deploy the Data Analyzer application on your organization's private server.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Security Overview](#security-overview)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Systemd Service Setup](#systemd-service-setup)
7. [Nginx Configuration (Optional)](#nginx-configuration)
8. [User Authentication Setup](#user-authentication-setup)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Security Checklist](#security-checklist)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ / RHEL 8+ / CentOS 8+
- **RAM**: Minimum 2GB (4GB recommended for 200-300 users)
- **CPU**: 2+ cores recommended
- **Disk**: 10GB+ free space
- **Python**: 3.8+

### Software to Install
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y

# RHEL/CentOS
sudo yum install python3 python3-pip nginx -y
```

---

## Security Overview

### ✅ Security Features Implemented

1. **Authentication**: Session-based login required for all pages
2. **Password Hashing**: Werkzeug SHA256 hashing
3. **Session Security**: HTTPOnly cookies, CSRF protection
4. **Input Validation**: All user inputs validated
5. **Error Handling**: Generic error messages (no sensitive info leaked)
6. **Logging**: All authentication attempts logged
7. **Secret Key**: Environment-based secret configuration
8. **Session Timeout**: 1-hour automatic logout

### 🔒 What Makes This Code Safe

✅ **No SQL Injection**: Uses pandas (no SQL queries)
✅ **No XSS**: Flask auto-escapes templates
✅ **No CSRF**: Session-based auth with secure cookies
✅ **No Code Injection**: No eval(), exec(), or dynamic imports
✅ **No File Upload**: Read-only Excel access
✅ **No External APIs**: Self-contained application
✅ **Authenticated Access**: All endpoints require login
✅ **Password Security**: Hashed passwords, no plaintext

---

## Installation Steps

### Step 1: Clone or Copy Project

```bash
# On your server, navigate to your deployment directory
cd /opt  # or /var/www or your preferred location

# If using git
git clone https://your-repo/Data-Playgroup.git
cd Data-Playgroup

# Or copy files via scp/rsync
scp -r Data-Playground/ user@server:/opt/
```

### Step 2: Create Virtual Environment

```bash
cd /opt/Data-Playgroup

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Create Logs Directory

```bash
mkdir -p logs
chmod 755 logs
```

---

## Configuration

### Step 1: Setup Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Generate a secure secret key
python3 -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')" >> .env

# Edit the .env file
nano .env
```

**Edit `.env` with your values:**
```bash
SECRET_KEY=your-generated-secret-key-here
DATA_FILE=/opt/Data-Playgroup/data.xlsx
FLASK_ENV=production
SESSION_COOKIE_SECURE=True  # If using HTTPS
LOG_LEVEL=INFO
```

### Step 2: Place Your Excel File

```bash
# Copy your organization's data file
cp /path/to/your/data.xlsx /opt/Data-Playgroup/data.xlsx

# Set proper permissions
chmod 600 data.xlsx
chown your_username:your_username data.xlsx
```

### Step 3: Configure User Accounts

**Option A: Simple In-App Users** (Current Setup)

Edit `app.py` lines 24-35 and add your users:

```python
USERS = {
    'john.doe': {
        'password': generate_password_hash('SecurePassword123!'),
        'role': 'admin',
        'name': 'John Doe'
    },
    'jane.smith': {
        'password': generate_password_hash('SecurePassword456!'),
        'role': 'user',
        'name': 'Jane Smith'
    }
    # Add more users as needed
}
```

**Option B: LDAP/Active Directory** (For Larger Organizations)

If your organization uses LDAP/AD, integrate with python-ldap:

```bash
pip install python-ldap3
```

See `LDAP_INTEGRATION.md` for detailed steps (to be created).

---

## Running the Application

### Test Run (Development Mode)

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python app.py
```

Visit: `http://your-server-ip:5000`

**⚠️ DO NOT use this in production!**

### Production Run with Gunicorn

```bash
# Activate virtual environment
source venv/bin/activate

# Run with gunicorn
gunicorn -c gunicorn_config.py app:app
```

This will:
- Run on port 5000
- Use multiple workers based on CPU cores
- Log to `logs/access.log` and `logs/error.log`
- Handle 200-300+ concurrent users

---

## Systemd Service Setup

Autostart the application on boot:

### Step 1: Edit Service File

```bash
# Edit the service file with your paths
nano data-analyzer.service
```

Update these lines:
```ini
User=your_actual_username
Group=your_actual_group
WorkingDirectory=/opt/Data-Playgroup
Environment="PATH=/opt/Data-Playgroup/venv/bin"
EnvironmentFile=/opt/Data-Playgroup/.env
ExecStart=/opt/Data-Playgroup/venv/bin/gunicorn -c gunicorn_config.py app:app
```

### Step 2: Install Service

```bash
# Copy service file to systemd
sudo cp data-analyzer.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable data-analyzer

# Start service
sudo systemctl start data-analyzer

# Check status
sudo systemctl status data-analyzer
```

### Service Management Commands

```bash
# Start
sudo systemctl start data-analyzer

# Stop
sudo systemctl stop data-analyzer

# Restart
sudo systemctl restart data-analyzer

# View logs
sudo journalctl -u data-analyzer -f
```

---

## Nginx Configuration (Optional but Recommended)

Nginx provides:
- **HTTPS/SSL termination**
- **Better performance**
- **Load balancing** (if needed later)
- **Static file serving**

### Step 1: Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/data-analyzer
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-server.your-org.com;  # Change this!

    # Redirect to HTTPS (if you have SSL)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Logging
    access_log /var/log/nginx/data-analyzer-access.log;
    error_log /var/log/nginx/data-analyzer-error.log;
}

# HTTPS Configuration (if you have SSL certificates)
# server {
#     listen 443 ssl http2;
#     server_name your-server.your-org.com;
#
#     ssl_certificate /path/to/cert.pem;
#     ssl_certificate_key /path/to/key.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#
#     location / {
#         proxy_pass http://127.0.0.1:5000;
#         # ... same proxy settings as above
#     }
# }
```

### Step 2: Enable Nginx Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/data-analyzer /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Step 3: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Or for specific IP range (recommended for internal server)
sudo ufw allow from 192.168.1.0/24 to any port 80
sudo ufw allow from 192.168.1.0/24 to any port 443
```

---

## User Authentication Setup

### Adding New Users

**Method 1: Edit app.py directly**

```python
# In app.py, add to USERS dictionary:
'new.user': {
    'password': generate_password_hash('NewUserPassword123!'),
    'role': 'user',  # or 'admin'
    'name': 'New User Name'
}
```

Then restart:
```bash
sudo systemctl restart data-analyzer
```

**Method 2: Create a user management script** (Advanced)

Create `add_user.py`:
```python
from werkzeug.security import generate_password_hash
import json

username = input("Username: ")
password = input("Password: ")
name = input("Full Name: ")
role = input("Role (admin/user): ")

hashed = generate_password_hash(password)
print(f"\nAdd this to USERS in app.py:")
print(f"'{username}': {{'password': '{hashed}', 'role': '{role}', 'name': '{name}'}},")
```

Run:
```bash
python add_user.py
```

### Password Policy Recommendations

1. Minimum 12 characters
2. Mix of uppercase, lowercase, numbers, symbols
3. Change passwords every 90 days
4. No password reuse
5. Use password manager

---

## Monitoring & Maintenance

### Monitoring Application Health

```bash
# Check if service is running
sudo systemctl status data-analyzer

# View real-time logs
tail -f logs/access.log
tail -f logs/error.log

# Check resource usage
top -p $(pgrep -f gunicorn)

# Check disk space
df -h
```

### Log Rotation

Create `/etc/logrotate.d/data-analyzer`:

```
/opt/Data-Playgroup/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 your_username your_username
    postrotate
        systemctl reload data-analyzer > /dev/null
    endscript
}
```

### Backup Strategy

```bash
# Create backup script: /opt/backup-data-analyzer.sh
#!/bin/bash
BACKUP_DIR="/opt/backups/data-analyzer"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup data file
cp /opt/Data-Playgroup/data.xlsx $BACKUP_DIR/data_$DATE.xlsx

# Backup application code
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /opt/Data-Playgroup --exclude=venv --exclude=logs

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $DATE"
```

Set up cron job:
```bash
sudo crontab -e
# Add: Daily backup at 2 AM
0 2 * * * /opt/backup-data-analyzer.sh >> /var/log/data-analyzer-backup.log 2>&1
```

---

## Security Checklist

Before going live, verify:

- [ ] Changed default passwords in app.py
- [ ] Generated secure SECRET_KEY in .env
- [ ] Set SESSION_COOKIE_SECURE=True (if using HTTPS)
- [ ] Configured firewall (ufw/iptables)
- [ ] Set proper file permissions (chmod 600 .env, data.xlsx)
- [ ] SSL/TLS certificates installed (if using HTTPS)
- [ ] Limited server access to organization network only
- [ ] Set up log monitoring and alerts
- [ ] Configured backup strategy
- [ ] Tested login/logout functionality
- [ ] Tested with 10-20 concurrent users
- [ ] Reviewed logs for errors
- [ ] Documented who has admin access
- [ ] Set up password rotation policy

---

## Troubleshooting

### App won't start

```bash
# Check logs
sudo journalctl -u data-analyzer -n 50

# Check if port is in use
sudo lsof -i :5000

# Check permissions
ls -la /opt/Data-Playgroup/
```

### Can't login

```bash
# Check user credentials in app.py
# Verify password hash
python3 -c "from werkzeug.security import check_password_hash; print(check_password_hash('hash', 'password'))"

# Check logs
tail -f logs/error.log
```

### Performance issues

```bash
# Check CPU/RAM usage
top

# Check worker count in gunicorn_config.py
# Increase workers if needed

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Data file not loading

```bash
# Check file exists
ls -la data.xlsx

# Check file permissions
sudo -u your_username cat data.xlsx

# Check DATA_FILE in .env matches actual path
cat .env | grep DATA_FILE
```

---

## Support & Contact

For issues or questions:

1. Check logs: `tail -f logs/error.log`
2. Review this guide
3. Contact your IT department
4. Check project README.md

---

## Security Incident Response

If you suspect a security breach:

1. **Immediately stop the service**: `sudo systemctl stop data-analyzer`
2. **Check logs for suspicious activity**: `grep -i "failed login" logs/error.log`
3. **Change all passwords and SECRET_KEY**
4. **Review access logs**: `cat logs/access.log`
5. **Contact security team**
6. **Restore from backup if necessary**

---

**Your application is now production-ready and secure!** 🎉🔒
