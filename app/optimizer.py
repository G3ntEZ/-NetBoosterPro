import subprocess
import logging

# Очистка DNS
def flush_dns():
    try:
        logging.info("Выполняется очистка DNS...")
        result = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            logging.info("DNS успешно очищен.")
            return "✅ DNS успешно очищен!"
        else:
            logging.error(f"Ошибка при очистке DNS: {result.stderr}")
            return f"❌ Ошибка: {result.stderr}"
    except Exception as e:
        logging.exception("Исключение при очистке DNS")
        return f"❌ Исключение: {e}"


# Универсальная установка DNS
def set_dns(interface_name="Ethernet", primary="1.1.1.1", secondary="1.0.0.1"):
    try:
        logging.info(f"Изменение DNS для {interface_name} на {primary}, {secondary}")
        subprocess.run(
            ["netsh", "interface", "ip", "set", "dns", f"name={interface_name}", "static", primary, "primary"],
            capture_output=True, text=True, shell=True
        )
        subprocess.run(
            ["netsh", "interface", "ip", "add", "dns", f"name={interface_name}", secondary, "index=2"],
            capture_output=True, text=True, shell=True
        )
        return f"✅ DNS успешно изменён на {primary} / {secondary}!"
    except Exception as e:
        logging.exception("Ошибка при изменении DNS")
        return f"❌ Ошибка: {e}"


# Готовые профили
def set_dns_cloudflare(interface_name="Ethernet"):
    return set_dns(interface_name, "1.1.1.1", "1.0.0.1")

def set_dns_google(interface_name="Ethernet"):
    return set_dns(interface_name, "8.8.8.8", "8.8.4.4")

def set_dns_auto(interface_name="Ethernet"):
    try:
        logging.info(f"Возврат автоматического DNS для {interface_name}")
        subprocess.run(
            ["netsh", "interface", "ip", "set", "dns", f"name={interface_name}", "source=dhcp"],
            capture_output=True, text=True, shell=True
        )
        return "✅ DNS возвращён на автоматический (DHCP)!"
    except Exception as e:
        logging.exception("Ошибка при возврате DNS")
        return f"❌ Ошибка: {e}"
