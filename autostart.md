### **1. Prepare Your Environment**
- Ensure Python 3 is installed on your Raspberry Pi. Verify it with:
  ```bash
  python3 --version
  ```
- Install `discord.py`:
  ```bash
  pip3 install discord.py
  ```
- Write your bot script and ensure it works correctly when run manually:
  ```bash
  python3 bot.py
  ```

---

### **2. Use a Supervisor Tool**
The `systemd` service or `pm2` (a process manager) can handle automatic restarts and ensure your bot starts when the Raspberry Pi boots.

#### **Option 1: Using systemd**
1. **Create a systemd Service File**:
   ```bash
   sudo nano /etc/systemd/system/discordbot.service
   ```

2. **Add the Following Configuration**:
   Replace `/path/to/bot.py` with the full path to your bot script.

   ```ini
    [Unit]
    Description=Discord Bot
    After=network-online.target
    Wants=network-online.target

    [Service]
    ExecStartPre=/bin/sleep 10
    ExecStart=/usr/bin/python3 /path/to/bot.py
    Restart=always
    User=pi
    WorkingDirectory=/path/to/
    StandardOutput=inherit
    StandardError=inherit

    [Install]
    WantedBy=multi-user.target
   ```

3. **Enable and Start the Service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable discordbot
   sudo systemctl start discordbot
   ```

4. **Check the Status**:
   ```bash
   sudo systemctl status discordbot
   ```
   This will show logs and let you confirm the bot is running.


---

### **3. Optional: Monitor Resource Usage**
For additional reliability, you can set up monitoring to check memory or CPU usage using tools like `htop` or custom scripts.

---

### **Troubleshooting**
- If your bot isn't starting:
  - Check logs using `sudo journalctl -u discordbot` (for `systemd`) or `pm2 logs discordbot`.
  - Verify permissions to the bot script directory.
- If your bot crashes often:
  - Add error handling to your bot script using `try/except` blocks to catch unhandled exceptions.

This setup will ensure your bot starts automatically, restarts on crashes, and provides logs for debugging.