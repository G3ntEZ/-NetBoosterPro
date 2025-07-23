import subprocess

def check_ping(host="8.8.8.8"):
    try:
        # Для Windows: -n 1 (один пакет), -w 1000 (таймаут 1 сек)
        result = subprocess.run(["ping", host, "-n", "1", "-w", "1000"],
                                capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            # Найдём время ответа
            for line in result.stdout.splitlines():
                if "Average" in line or "Среднее" in line:
                    return int(''.join(filter(str.isdigit, line.split('=')[-1])))
            return 1  # если не нашли, но ответ есть
        else:
            return None  # нет ответа
    except Exception:
        return None
