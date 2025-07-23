import threading
import time
import subprocess
from app.optimizer import set_dns_cloudflare, set_dns_google
# функция update_status будет передаваться из main_window

class AutoOptimizer:
    def __init__(self, status_callback):
        self.status_callback = status_callback
        self.running = False
        self.thread = None
        self.interval = 30  # интервал проверки в секундах

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        self.status_callback("✅ Авто-режим запущен (проверка каждые 30 секунд)")

    def stop(self):
        self.running = False
        self.status_callback("⏹ Авто-режим остановлен")

    def run(self):
        current_dns = "cloudflare"
        set_dns_cloudflare()
        self.status_callback("🌐 Используется DNS Cloudflare")

        while self.running:
            try:
                ping_cf = self.ping_host("1.1.1.1")
                ping_google = self.ping_host("8.8.8.8")

                self.status_callback(f"📡 Пинг Cloudflare: {ping_cf} ms | Google: {ping_google} ms")

                if ping_google < ping_cf - 10 and current_dns != "google":
                    set_dns_google()
                    current_dns = "google"
                    self.status_callback("🔄 Переключение на Google DNS (лучший пинг)")

                elif ping_cf < ping_google - 10 and current_dns != "cloudflare":
                    set_dns_cloudflare()
                    current_dns = "cloudflare"
                    self.status_callback("🔄 Переключение на Cloudflare DNS (лучший пинг)")

            except Exception as e:
                self.status_callback(f"⚠️ Ошибка авто-режима: {e}")

            time.sleep(self.interval)

    def ping_host(self, host):
        # Пингуем 1 раз, ждём максимум 1 секунду
        try:
            output = subprocess.run(["ping", "-n", "1", "-w", "1000", host],
                                    capture_output=True, text=True, timeout=3)
            result = output.stdout
            # Ищем время в ms
            for line in result.splitlines():
                if "Среднее" in line or "Average" in line:
                    ms = line.split("=")[-1].replace("ms", "").replace("мс", "").strip()
                    return int(ms)
            # если не нашли строку со временем
            return 999
        except:
            return 999
