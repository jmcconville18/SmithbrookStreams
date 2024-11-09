import psutil
from flask import Blueprint, jsonify
import paramiko

metrics_bp = Blueprint('metrics', __name__)

VPS_IP = '198.12.80.190'
VPS_USER = 'jmcconville'
VPS_KEY_PATH = '/home/joe/.ssh/id_rsa'

def get_local_metrics():
    try:
        return {
            "cpu": psutil.cpu_percent(interval=0.1),  # Reduce interval to avoid blocking
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent
        }
    except Exception as e:
        print(f"Error fetching local metrics: {e}")
        return {"cpu": None, "memory": None, "disk": None}

def get_joedrive_metrics():
    try:
        return {"disk": psutil.disk_usage('/mnt/JoeDrive').percent}
    except Exception as e:
        print(f"Error fetching JoeDrive metrics: {e}")
        return {"disk": None}

def get_vps_metrics():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VPS_IP, username=VPS_USER, key_filename=VPS_KEY_PATH, timeout=5)
        stdin, stdout, stderr = client.exec_command("free -m && df -h && uptime")
        output = stdout.read().decode()
        client.close()
        return {"vps_output": output}
    except Exception as e:
        print(f"Error fetching VPS metrics: {e}")
        return {"vps_output": "Error retrieving VPS metrics"}

@metrics_bp.route('/api/metrics')
def api_metrics():
    local_metrics = get_local_metrics()
    joedrive_metrics = get_joedrive_metrics()
    vps_metrics = get_vps_metrics()
    
    return jsonify({
        "local": local_metrics,
        "joedrive": joedrive_metrics,
        "vps": vps_metrics
    })

