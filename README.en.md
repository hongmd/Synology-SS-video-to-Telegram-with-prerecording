![](/images/4logo.png)
# Synology Surveillance Station Video to Telegram with Pre-recording

Send video with pre-recording from Synology Surveillance Station motion detector to Telegram using Webhook automation.

The first video includes pre-recording, subsequent videos are sent every 10 seconds until motion detection ends.

[![Donate](https://img.shields.io/badge/donate-Yandex-red.svg)](https://yoomoney.ru/fundraise/b8GYBARCVRE.230309)
![](https://img.shields.io/github/watchers/samoswall/Synology-Surveillance-Station-video-to-Telegram-with-prerecording.svg)
![](https://img.shields.io/github/stars/samoswall/Synology-Surveillance-Station-video-to-Telegram-with-prerecording.svg)

![](https://badgen.net/static/API/Telegram)
![](https://badgen.net/static/API/Synology%20Surveillance%20Station)
![](https://badgen.net/static/Made%20with/Python)

## Table of Contents
- [Quick Start with Docker Compose](#quick-start-with-docker-compose)
- [Installation via Docker Run](#installation-via-docker-run)
- [Manual Docker Setup](#manual-docker-setup)
- [Environment Variables](#environment-variables)
- [Synology Configuration](#synology-configuration)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

## Quick Start with Docker Compose

The easiest way to get started is using Docker Compose.

1. **Clone the repository:**
```bash
git clone https://github.com/samoswall/Synology-Surveillance-Station-video-to-Telegram-with-prerecording.git
cd Synology-Surveillance-Station-video-to-Telegram-with-prerecording
```

2. **Create `.env` file from template:**
```bash
cp .env.example .env
```

3. **Edit `.env` file with your configuration:**
```bash
nano .env
# Or use your preferred text editor
```

4. **Update `docker-compose.yaml`:**
   - Change `/home/test/:/bot` path to your desired directory for storing configs
   - This is where `syno_cam_config.json` will be stored

5. **Start the container:**
```bash
docker-compose up -d
```

6. **Check logs:**
```bash
docker-compose logs -f
```

## Installation via Docker Run

If you prefer using `docker run` instead:

```bash
docker run -d \
  --name VideoSsToTg \
  --restart unless-stopped \
  -p 7878:7878 \
  -e "TG_CHAT_ID=123456" \
  -e "TG_TOKEN=1234567890:AAAAAAbbbbbbCCCC1234567890abcdefgh" \
  -e "SYNO_IP=192.168.1.1" \
  -e "SYNO_PORT=5000" \
  -e "SYNO_LOGIN=admin" \
  -e "SYNO_PASS=password" \
  -v /your/storage/path:/bot \
  striker72rus/ss_to_tg_video:latest
```

## Manual Docker Setup

### Building the Image

```bash
docker build -t ss_to_tg_video .
```

### Running the Container

```bash
docker run -d \
  --name VideoSsToTg \
  --restart unless-stopped \
  -p 7878:7878 \
  -e TG_CHAT_ID=your_chat_id \
  -e TG_TOKEN=your_bot_token \
  -e SYNO_IP=192.168.1.1 \
  -e SYNO_PORT=5000 \
  -e SYNO_LOGIN=admin \
  -e SYNO_PASS=password \
  -v /your/path:/bot \
  ss_to_tg_video
```

## Environment Variables

All environment variables are **required** unless noted as optional.

| Variable | Description | Example |
|----------|-------------|---------|
| `TG_CHAT_ID` | Telegram Chat ID where notifications are sent | `1234567890` |
| `TG_TOKEN` | Telegram Bot Token (get from [@BotFather](https://t.me/BotFather)) | `0987654321:AABBCCDDEEFFGGaabbccddeeffgg` |
| `SYNO_IP` | IP address of your Synology NAS | `192.168.1.177` |
| `SYNO_PORT` | DSM port number (default is 5000) | `5000` |
| `SYNO_LOGIN` | Synology username | `admin` |
| `SYNO_PASS` | Synology password | `mypassword` |
| `SYNO_OTP` | **Optional:** OTP code for 2FA | `079444` |

### Getting Telegram Bot Token

1. Open Telegram and find [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions and save your bot token
4. Find your Chat ID using [@userinfobot](https://t.me/userinfobot)

### Getting Synology IP and Port

1. Open Synology DSM in browser
2. Check Settings → Network → General for IP address
3. Default port is 5000, but can be configured differently

## Synology Configuration

### Step 1: Create Automation Webhook

1. Open **Control Panel** → **Security** → **Access Control** → **Application**
2. Enable external device access if needed
3. Go to **Surveillance Station** → **Settings** → **Integration** → **Webhooks**

### Step 2: Add Webhook

1. In Webhooks section, click **Add**
2. Configure webhook:
   - **Name:** "Video to Telegram" (or any name)
   - **URL:** `http://your-docker-host:7878/webhookcam`
   - **Method:** POST
   - **Format:** JSON

### Step 3: Configure Motion Detection

1. Go to **Surveillance Station** → **Settings** → **Schedule**
2. For each camera, configure motion detection triggers
3. Under **Advanced** → **Webhooks**, select your created webhook

### Step 4: Initial Configuration Message

When the container starts for the first time:
1. It will automatically log into Synology
2. It will fetch all camera configurations
3. You'll receive a Telegram message with camera list:
```
Cameras config:
CamId: 1 IP: 192.168.1.196 SynoName: Front Door Model: Define Vendor: User
CamId: 2 IP: 192.168.1.187 SynoName: Back Yard Model: Define Vendor: User
```

**Note:** The `CamId` values are used for motion detection configuration in Synology.

## Using Makefile Commands

```bash
# Build Docker image
make build

# Start containers
make up

# Stop containers
make down

# View logs
make logs

# Clean everything
make clean

# Build and run
make build-run

# Restart containers
make restart
```

## Troubleshooting

### Container Won't Start

1. **Check if port 7878 is already in use:**
   ```bash
   docker ps -a
   netstat -an | grep 7878
   ```

2. **Check container logs:**
   ```bash
   docker logs VideoSsToTg
   ```

### No Message Received

1. **Verify environment variables:**
   ```bash
   docker inspect VideoSsToTg | grep -A 50 "Env"
   ```

2. **Check if config file exists:**
   - SSH into Synology and check the `/bot` folder for `syno_cam_config.json`

3. **Two-factor authentication timeout:**
   - If using 2FA, the container must be started within 60 seconds of setting `SYNO_OTP`
   - Delete `syno_cam_config.json` if configuration changes

### Camera Configuration Changed

1. Delete `syno_cam_config.json` from the storage volume
2. Restart the container:
   ```bash
   docker restart VideoSsToTg
   ```

### Invalid Credentials

1. Verify your Synology username and password are correct
2. Ensure the user has access to Surveillance Station
3. If 2FA is enabled, make sure you're using the correct format

## Security Recommendations

1. **Use strong passwords** for Synology accounts
2. **Enable two-factor authentication** for extra security
3. **Don't commit `.env` file** to version control (it's already in `.gitignore`)
4. **Use a dedicated Synology account** with limited permissions if possible
5. **Verify the webhook URL** is only accessible from trusted network

## Deployment on Synology DSM

### Method 1: Synology Registry (Recommended)

1. Open **Package Center** → **Settings** → **Enable user-defined repository**
2. Add custom registry with this application
3. Search for "ss_to_tg_video" and install

### Method 2: Manual Docker Setup

1. SSH into Synology:
   ```bash
   ssh admin@your-synology-ip
   ```

2. Create directory for storage:
   ```bash
   mkdir -p /volume1/docker/ss_to_tg_video
   ```

3. Run the container (see Installation section above)

## Support

- 🐛 **Report Issues:** Create an issue on [GitHub](https://github.com/samoswall/Synology-Surveillance-Station-video-to-Telegram-with-prerecording/issues)
- 💬 **Discussions:** Use GitHub Discussions for questions
- 📖 **Documentation:** Check the README.md for Russian version

## License

This project is open source and available under the [MIT License](LICENSE).

## Changelog

### v1.0.0
- Initial release
- Docker Compose support
- Two-factor authentication support
- Video pre-recording with 10-second intervals

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Donations

If this project helped you, consider supporting it:

[![Donate](https://img.shields.io/badge/donate-Yandex-red.svg)](https://yoomoney.ru/fundraise/b8GYBARCVRE.230309)

## Credits

- Original author: [samoswall](https://github.com/samoswall)
- Forked and improved by: [hongmd](https://github.com/hongmd)
- Contributors: [See all contributors](https://github.com/samoswall/Synology-Surveillance-Station-video-to-Telegram-with-prerecording/graphs/contributors)

## FAQ

**Q: Can I use this with multiple cameras?**  
A: Yes! The application automatically detects all cameras configured in Synology Surveillance Station.

**Q: What's the video format?**  
A: MP4 files, default 10 seconds per segment.

**Q: Can I change the video duration?**  
A: Yes, modify the `playTimeMs` parameter in `src/main.py` (currently set to 10000ms = 10 seconds).

**Q: Is the password stored securely?**  
A: No, it's stored in environment variables. Use strong passwords and limit account permissions.

**Q: Can I run multiple instances?**  
A: Yes, use different ports and storage volumes for each instance.

---

**Last Updated:** October 30, 2025

For the Russian version, see [README.md](README.md)
