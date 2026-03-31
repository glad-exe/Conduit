# 🛠️ Conduit
> A modular Python-based Discord bot for home lab orchestration and service management.

Conduit acts as a Discord interface for your self-hosted home lab environment. It is designed with a **plugin-first architecture**, allowing for seamless integration with media servers, game servers, and system monitoring.

---

## 🚀 Features

### 🎬 Media Management
* **Jellyfin & Sonarr:** Direct integration to manage show requests, and provide a passwordless connection to Jellyfin.
* **Metadata Fetching:** Real-time querying for series and movie information.

### 🎮 Game Server Control
* **Minecraft Integration:** RCON-based command execution, player count tracking, and automated server toggles.

### 🖥️ System & Home Lab
* **Modular Design:** Each service exists as a standalone "plug", making it easy to add or remove features without breaking the core bot.
* **Linux Optimized:** Tailored for performance and low overhead on Linux-based home lab setups.

---

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Framework:** `discord.py` (Cogs-based architecture)
* **Integrations:** Jellyfin API, Sonarr API, Minecraft RCON
* **Environment:** Linux (Home Lab)

---
## 🚀 Upcoming Features
### Short term:
* **Flexible Server Module:** Biggest change! Converting the Minecraft cog into a general server module. Will be able to handle every server you have. 
* **Plex support:** Adding a secondary media provider module.
* **Temperature Alerts:** Automated Discord notification if the server core gets too hot.

### Long term:
* **Hardware Support:** Adding Arduino and esp32 support.
* **Automated Backups:** Automatically back up your server metadata.
* **Credential Management**: Will use VaultWarden to avoid `.env` dependency by fetching environment variables at runtime via encrypted vault queries.

