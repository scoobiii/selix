#!/usr/bin/env python3
import psutil
import platform
import json

def get_hardware_info():
    info = {
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count_logical": psutil.cpu_count(),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "swap_total_gb": round(psutil.swap_memory().total / (1024**3), 1),
        "disk_usage_percent": psutil.disk_usage('/').percent,
    }
    # Temperatura (se disponível)
    try:
        temps = psutil.sensors_temperatures()
        for key in ('cpu-thermal', 'cpu_thermal', 'coretemp'):
            if key in temps and temps[key]:
                info["cpu_temperature_c"] = temps[key][0].current
                break
    except:
        pass
    return info

if __name__ == "__main__":
    info = get_hardware_info()
    print(json.dumps(info, indent=2))
