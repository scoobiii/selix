# tests/hardware_profile.py
import psutil
import platform
import os

def get_hardware_profile():
    """
    Retorna dicionário com características do hardware.
    """
    profile = {
        "system": platform.system(),
        "machine": platform.machine(),
        "cpu_count_logical": psutil.cpu_count(),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "disk_type": "ssd" if psutil.disk_usage('/').total < 2**40 else "hdd",  # simplificado
    }
    # GPU detection (tentativa)
    gpu_available = False
    try:
        # NVIDIA
        import subprocess
        result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            profile["gpu"] = result.stdout.strip().split('\n')[0]
            gpu_available = True
    except:
        pass
    if not gpu_available:
        try:
            import torch
            if torch.cuda.is_available():
                profile["gpu"] = "CUDA"
                gpu_available = True
        except:
            pass
    if not gpu_available:
        profile["gpu"] = None
    # Perfil de velocidade
    # Baixo: RAM < 4GB ou CPU < 4 núcleos
    # Médio: RAM 4-8GB e CPU >= 4
    # Alto: RAM >= 8GB e CPU >= 8
    if profile["ram_gb"] < 4 or profile["cpu_count_logical"] < 4:
        profile["speed"] = "low"
        profile["suggested_timeout"] = 90
        profile["suggested_parallel_workers"] = 1
    elif profile["ram_gb"] < 8:
        profile["speed"] = "medium"
        profile["suggested_timeout"] = 60
        profile["suggested_parallel_workers"] = min(profile["cpu_count_logical"], 2)
    else:
        profile["speed"] = "high"
        profile["suggested_timeout"] = 30
        profile["suggested_parallel_workers"] = min(profile["cpu_count_logical"], 4)
    return profile

