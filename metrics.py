import psutil
from flask import Blueprint, jsonify
import paramiko

metrics_bp = Blueprint('metrics', __name__)

VPS_IP = '150.136.87.31'
VPS_USER = 'opc'
VPS_KEY_PATH = '/home/joe/.ssh/id_rsa'

def get_local_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

def get_joedrive_metrics():
    return {"disk": psutil.disk_usage('/mnt/JoeDrive').percent}

def get_vps_metrics():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_IP, username=VPS_USER, key_filename=VPS_KEY_PATH)
    stdin, stdout, stderr = client.exec_command("free -m && df -h && uptime")
    output = stdout.read().decode()
    client.close()
    return {"vps_output": output}

@metrics_bp.route('/api/metrics')
def api_metrics():
    return jsonify({
        "local": get_local_metrics(),
        "joedrive": get_joedrive_metrics(),
        "vps": get_vps_metrics()
    })

