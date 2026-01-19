# Setting Up HUD Display as a System Service

This guide shows how to run `main.py` as a systemd service that starts automatically when the Raspberry Pi boots.

## Prerequisites

1. Make sure your virtual environment is set up and dependencies are installed:
   ```bash
   cd ~/hudler
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Test that the application works manually first:
   ```bash
   source venv/bin/activate
   python main.py
   ```

## Installation Steps

### 1. Edit the Service File

Edit `hudler.service` and update the paths if needed:

- `WorkingDirectory`: Should point to your hudler directory (e.g., `/home/pi/hudler`)
- `ExecStart`: Should point to your Python executable and main.py
- `User`: Change from `pi` if you're using a different user
- Environment variables: Uncomment and set as needed

**Option A: Using .env file (recommended)**
```ini
EnvironmentFile=/home/pi/hudler/.env
```

**Option B: Set environment variables directly in service file**
```ini
Environment="DISPLAY_TYPE=pico"
Environment="SIGNAL_PATH=http://172.28.1.64:8000/api/v1/asset/signals/"
Environment="SIGNAL_NAME=VDM_VehicleSpeed"
Environment="PICO_SERIAL_PORT=/dev/ttyACM0"
```

### 2. Copy Service File to Systemd Directory

```bash
sudo cp hudler.service /etc/systemd/system/
```

### 3. Reload Systemd

```bash
sudo systemctl daemon-reload
```

### 4. Enable the Service (Start on Boot)

```bash
sudo systemctl enable hudler.service
```

### 5. Start the Service

```bash
sudo systemctl start hudler.service
```

### 6. Check Service Status

```bash
sudo systemctl status hudler.service
```

## Useful Commands

### View Logs
```bash
# View recent logs
sudo journalctl -u hudler.service -n 50

# Follow logs in real-time
sudo journalctl -u hudler.service -f

# View logs since boot
sudo journalctl -u hudler.service -b
```

### Stop the Service
```bash
sudo systemctl stop hudler.service
```

### Restart the Service
```bash
sudo systemctl restart hudler.service
```

### Disable Auto-Start on Boot
```bash
sudo systemctl disable hudler.service
```

### Remove the Service
```bash
sudo systemctl stop hudler.service
sudo systemctl disable hudler.service
sudo rm /etc/systemd/system/hudler.service
sudo systemctl daemon-reload
```

## Troubleshooting

### Service Won't Start

1. Check the service status:
   ```bash
   sudo systemctl status hudler.service
   ```

2. Check logs for errors:
   ```bash
   sudo journalctl -u hudler.service -n 100
   ```

3. Verify paths are correct:
   ```bash
   ls -la /home/pi/hudler/venv/bin/python
   ls -la /home/pi/hudler/main.py
   ```

4. Test the command manually:
   ```bash
   cd /home/pi/hudler
   source venv/bin/activate
   python main.py
   ```

### Permission Issues

If you see permission errors:

1. Make sure the service file has correct user:
   ```bash
   # Edit the service file and change User=pi to your username
   sudo nano /etc/systemd/system/hudler.service
   sudo systemctl daemon-reload
   sudo systemctl restart hudler.service
   ```

2. For serial port access (Pico), you may need to add the user to the dialout group:
   ```bash
   sudo usermod -a -G dialout pi
   # Log out and back in for changes to take effect
   ```

### Virtual Environment Not Found

Make sure the path to your virtual environment Python is correct:
```bash
which python  # When venv is activated
# Use this full path in ExecStart
```

### Environment Variables Not Loading

1. If using `.env` file, make sure the path is correct in the service file
2. If setting directly, uncomment and set the Environment lines
3. Check that variables are loaded:
   ```bash
   sudo systemctl show hudler.service | grep Environment
   ```

## Testing After Setup

1. Reboot the Pi:
   ```bash
   sudo reboot
   ```

2. After reboot, check that the service started:
   ```bash
   sudo systemctl status hudler.service
   ```

3. Check logs to verify it's working:
   ```bash
   sudo journalctl -u hudler.service -f
   ```

