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
* **Flexible Server Module:** An All-In-One module, capable of handling every server and service. 
* **Modular Design:** Each service exists as a standalone "plug", making it easy to add or remove features without breaking the core bot.
* **Linux Optimized:** Tailored for performance and low overhead on Linux-based home lab setups.
  
---

## 🧩 Modules (Cogs)
Conduit is built modularly. You can enable or disable specific cogs in the `main.py` file depending on what your home lab requires.

### 🛠️ ServiceManager
Handles the starting, stopping, and monitoring of host-level background processes.
**Commands:**
* `svc-start <name>`: Boots up a configured service.
* `svc-stop <name>`: Gracefully terminates a running service, and kills them if they hang.
* `svc-exec <name> <cmd>`: Pipes commands directly into the active console.

### ⛏️ Minecraft Server Manager (`MinecraftCog`)
A dedicated module for managing, monitoring, and playing on a local Java Edition Minecraft server directly through Discord. It streams console outputs in real-time and uses `mcstatus` to ping the server for live player counts.
**Commands:**
* `mc-start` / `!mc-stop`: Safely boots up or saves and terminates the Minecraft server.
* `console <command>`: Executes an in-game command directly into the server console (Admin only).
* `mc-status`: Displays a live dashboard showing server uptime, active player count, and version.
* `ip`: Displays the server's connection address and port.
* `mc-mods`: Provides a direct download link to the current server modpack.

### 📺 Sonarr Media Requests (`SonarrCog`)
A seamless integration with your local Sonarr instance. This module allows users to search for and request TV shows directly from Discord. If a match is found on TVDB, it automatically adds the series to your Sonarr library and triggers your download client (e.g., qBittorrent) to grab missing episodes.
**Commands:**
* `sonarr-request <show_name>`: Searches Sonarr for the specified show. If it isn't already in your library, it adds it and begins searching for episodes automatically.

### 🍿 Jellyfin Quick Connect (JellyfinCog)
A custom authentication module that allows users in your Discord server to automatically create and log into your Jellyfin media server without needing to remember a password. It maps a user's Discord ID to a new Jellyfin account and authorizes their TV/mobile device remotely via Quick Connect codes.

`jf-signup <username>`: Instantly creates a new, passwordless Jellyfin account mapped to your Discord ID.

`jf-login <code>`: Authorizes a 6-digit Jellyfin Quick Connect code displayed on your TV or mobile app, logging you in automatically.

### 💻 System & Core Utilities (SystemCog)
The foundational module for Conduit. This cog handles basic bot functionality, dynamic help menus, and provides a real-time hardware monitoring dashboard for the host machine.
* `device-status`: Returns a live dashboard of the host machine's hardware, including CPU load, RAM usage, CPU temperature, and battery status (useful if running on a laptop).
* `help`: Dynamically generates a help menu listing all available commands and their descriptions across all loaded cogs.
* `ping`: A simple latency check.

---

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Framework:** `discord.py` (Cogs-based architecture)
* **Integrations:** Jellyfin API, Sonarr API, Minecraft RCON
* **Environment:** Linux (Home Lab)

---
## 🚀 Upcoming Features
### Short term:
* **Plex support:** Adding a secondary media provider module.
* **Temperature Alerts:** Automated Discord notification if the server core gets too hot.

### Long term:
* **Hardware Support:** Adding Arduino and esp32 support.
* **Automated Backups:** Automatically back up your server metadata.
* **Credential Management**: Will use VaultWarden to avoid `.env` dependency by fetching environment variables at runtime via encrypted vault queries.

