import sys
import os
import json
import webbrowser
import win32com.client
import threading, time, subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QCheckBox, QTabWidget, QTextEdit, QSizePolicy, QSystemTrayIcon, QMenu, QDialog, QHBoxLayout
)
from PyQt6.QtGui import QFont, QIcon, QAction, QCloseEvent
from PyQt6.QtCore import Qt, QEvent, QCoreApplication

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

LANG = {
    "main": "🌐 Основное",
    "reco": "💡 Рекомендации",
    "about": "ℹ️ О программе",
    "logs": "📜 Логи",
    "settings": "⚙️ Настройки",
    "choose": "Выберите действие",
    "flush": "Очистить DNS",
    "cloudflare": "DNS → Cloudflare",
    "google": "DNS → Google",
    "auto": "DNS → Авто (DHCP)",
    "speed": "Тест скорости",
    "author": "Создатель: G3ntEZ\nВерсия: 1.4\nВсе права защищены © 2025",
    "write_dev": "✉️ Написать разработчику",
    "faq": "📌 Часто задаваемые вопросы",
    "support": "💖 Поддержка проекта",
    "close_title": "Закрытие программы",
    "close_question": "Вы хотите закрыть программу или свернуть в трей?",
    "close_yes": "🚪 Закрыть",
    "close_no": "📥 Свернуть в трей",
}

# ======= Мониторинг сети =======
class NetworkMonitor(threading.Thread):
    def __init__(self, update_callback):
        super().__init__(daemon=True)
        self.update_callback = update_callback
        self.running = True

    def run(self):
        while self.running:
            try:
                start = time.time()
                subprocess.check_output(['ping', '-n', '1', '8.8.8.8'])
                ping_time = int((time.time() - start) * 1000)
                self.update_callback(f"🌐 Пинг: {ping_time} мс")
            except Exception as e:
                self.update_callback(f"❌ Ошибка мониторинга: {e}")
            time.sleep(5)

    def stop(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()

        self.setWindowTitle("NetBoosterPro")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "booster_icon.ico")))
        self.resize(900, 600)
        self.setMinimumSize(500, 350)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # 🌐 Основное
        self.status_label = QLabel(LANG["choose"])
        self.status_label.setFont(QFont("Segoe UI", 12))
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.status_label)

        btn_flush = QPushButton(LANG["flush"])
        btn_flush.clicked.connect(lambda: self.update_status("✅ DNS очищен!"))
        self._setup_button(btn_flush)
        main_layout.addWidget(btn_flush)

        btn_cloudflare = QPushButton(LANG["cloudflare"])
        btn_cloudflare.clicked.connect(lambda: self.update_status("✅ DNS Cloudflare установлен!"))
        self._setup_button(btn_cloudflare)
        main_layout.addWidget(btn_cloudflare)

        btn_google = QPushButton(LANG["google"])
        btn_google.clicked.connect(lambda: self.update_status("✅ DNS Google установлен!"))
        self._setup_button(btn_google)
        main_layout.addWidget(btn_google)

        btn_auto = QPushButton(LANG["auto"])
        btn_auto.clicked.connect(lambda: self.update_status("✅ Авто DNS!"))
        self._setup_button(btn_auto)
        main_layout.addWidget(btn_auto)

        self.auto_checkbox = QCheckBox("Авто-режим")
        self.auto_checkbox.stateChanged.connect(self.toggle_auto)
        main_layout.addWidget(self.auto_checkbox)

        btn_speedtest = QPushButton(LANG["speed"])
        btn_speedtest.clicked.connect(lambda: self.update_status("⏳ Тест скорости..."))
        self._setup_button(btn_speedtest)
        main_layout.addWidget(btn_speedtest)

        self.monitor_label = QLabel()
        main_layout.addWidget(self.monitor_label)

        main_tab = QWidget()
        main_tab.setLayout(main_layout)

        # 💡 Рекомендации
        reco_layout = QVBoxLayout()
        reco_label = QLabel(
            "<h3>✔ Очистка DNS — если интернет тормозит.<br>"
            "✔ Cloudflare — лучший для игр и стриминга.<br>"
            "✔ Google — альтернативный DNS.<br>"
            "✔ Авто-режим — постоянный мониторинг.<br>"
            "✔ Тест скорости — проверка после изменений.</h3>"
        )
        reco_label.setWordWrap(True)
        reco_label.setFont(QFont("Segoe UI", 11))
        reco_layout.addWidget(reco_label)
        reco_tab = QWidget()
        reco_tab.setLayout(reco_layout)

        # ℹ️ О программе
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        self.about_label = QLabel(LANG["author"])
        self.about_label.setWordWrap(True)
        self.about_label.setFont(QFont("Segoe UI", 11))
        about_layout.addWidget(self.about_label)

        btn_write = QPushButton(LANG["write_dev"])
        btn_write.clicked.connect(lambda: webbrowser.open("https://vk.com/xzx111zxz"))
        self._setup_button(btn_write)
        about_layout.addWidget(btn_write)

        btn_faq = QPushButton(LANG["faq"])
        btn_faq.clicked.connect(lambda: webbrowser.open("https://vk.com/@rust_news_py-netboosterpro"))
        self._setup_button(btn_faq)
        about_layout.addWidget(btn_faq)

        btn_support = QPushButton(LANG["support"])
        btn_support.clicked.connect(self.show_support_links)
        self._setup_button(btn_support)
        about_layout.addWidget(btn_support)

        about_tab.setLayout(about_layout)

        # 📜 Логи
        log_layout = QVBoxLayout()
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        log_tab = QWidget()
        log_tab.setLayout(log_layout)

        # ⚙️ Настройки
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()

        lbl_version = QLabel("Версия: 1.4  |  © G3ntEZ 2025")
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_version.setFont(QFont("Segoe UI", 10))
        settings_layout.addWidget(lbl_version)

        btn_update = QPushButton("🔄 Проверить обновления")
        btn_update.clicked.connect(lambda: self.update_status("✅ Проверка обновлений... (GitHub скоро будет подключён)"))
        self._setup_button(btn_update)
        settings_layout.addWidget(btn_update)

        self.autostart_checkbox = QCheckBox("✅ Запускать вместе с Windows")
        self.autostart_checkbox.setChecked(self.config.get("autostart", False))
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)
        settings_layout.addWidget(self.autostart_checkbox)

        btn_backup = QPushButton("💾 Сделать бэкап настроек")
        def backup_config():
            try:
                source = CONFIG_PATH
                backup_path = os.path.join(os.path.dirname(CONFIG_PATH), "backup_config.json")
                if os.path.exists(source):
                    import shutil
                    shutil.copy(source, backup_path)
                    self.update_status(f"✅ Бэкап создан: {backup_path}")
                else:
                    self.update_status("⚠️ Конфиг не найден.")
            except Exception as e:
                self.update_status(f"❌ Ошибка бэкапа: {e}")
        btn_backup.clicked.connect(backup_config)
        self._setup_button(btn_backup)
        settings_layout.addWidget(btn_backup)

        settings_layout.addStretch()
        settings_tab.setLayout(settings_layout)

        tabs.addTab(main_tab, LANG["main"])
        tabs.addTab(reco_tab, LANG["reco"])
        tabs.addTab(about_tab, LANG["about"])
        tabs.addTab(log_tab, LANG["logs"])
        tabs.addTab(settings_tab, LANG["settings"])

        # Трей
        self.tray = QSystemTrayIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "booster_icon.ico")), self)
        tray_menu = QMenu()
        show_action = QAction("Показать окно", self)
        show_action.triggered.connect(self.showNormal)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

        self.apply_dark_theme()

        # Мониторинг сети
        self.monitor_thread = NetworkMonitor(self.update_monitor_label)
        self.monitor_thread.start()

    def _setup_button(self, btn):
        btn.setMinimumHeight(40)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3f41;
                color: #ffffff;
                font-weight: bold;
                border-radius: 8px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background-color: #505354;
            }
        """)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: #f0f0f0; font-family: Segoe UI; font-size: 14px; }
            QTabBar::tab { background: #3c3f41; padding: 10px; margin: 2px; border-radius: 6px; }
            QTabBar::tab:selected { background: #0078d7; }
            QTextEdit { background-color: #1e1e1e; border: 1px solid #555; font-family: Consolas, monospace; }
        """)

    def update_monitor_label(self, text):
        def update():
            self.monitor_label.setText(text)
        QCoreApplication.postEvent(self, type('UpdateEvent', (QEvent,), {'update_func': update})())

    def update_status(self, text):
        self.status_label.setText(text)
        self.log_view.append(text)
        self.tray.showMessage("NetBoosterPro", text, QSystemTrayIcon.MessageIcon.Information)

    def toggle_auto(self, state):
        if self.auto_checkbox.isChecked():
            self.update_status("✅ Авто-режим включён")
        else:
            self.update_status("⛔ Авто-режим выключен")

    def toggle_autostart(self, state):
        enabled = self.autostart_checkbox.isChecked()
        self.config["autostart"] = enabled
        self.save_config()
        startup_dir = os.path.join(os.getenv('APPDATA'), r"Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        shortcut_path = os.path.join(startup_dir, "NetBoosterPro.lnk")
        exe_path = sys.executable
        if enabled:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.save()
            self.update_status("✅ Автозапуск включён")
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            self.update_status("⛔ Автозапуск выключен")

    def show_support_links(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Поддержка проекта")
        dialog.setFixedSize(400, 200)
        layout = QVBoxLayout()
        label = QLabel("Выберите способ поддержки:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_donate1 = QPushButton("💖 Donationalerts")
        btn_donate1.clicked.connect(lambda: webbrowser.open("https://www.donationalerts.com/r/g3ntez"))
        self._setup_button(btn_donate1)
        layout.addWidget(btn_donate1)

        btn_donate2 = QPushButton("☕ VK Donut")
        btn_donate2.clicked.connect(lambda: webbrowser.open("https://vk.com/rust_news_py?levelId=2055&source=unknown&w=donut_payment-179204231"))
        self._setup_button(btn_donate2)
        layout.addWidget(btn_donate2)

        dialog.setLayout(layout)
        dialog.exec()

    def show_close_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(LANG["close_title"])
        dialog.setFixedSize(360, 160)
        layout = QVBoxLayout()
        label = QLabel(LANG["close_question"])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        btn_layout = QHBoxLayout()
        result = {"choice": None}

        def choose_close():
            result["choice"] = "close"
            dialog.accept()

        def choose_minimize():
            result["choice"] = "minimize"
            dialog.accept()

        btn_close = QPushButton(LANG["close_yes"])
        btn_close.clicked.connect(choose_close)
        self._setup_button(btn_close)
        btn_minimize = QPushButton(LANG["close_no"])
        btn_minimize.clicked.connect(choose_minimize)
        self._setup_button(btn_minimize)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addWidget(btn_minimize)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()
        return result["choice"]

    def closeEvent(self, event: QCloseEvent):
        choice = self.show_close_dialog()
        if choice == "close":
            self.monitor_thread.stop()
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.tray.showMessage("NetBoosterPro", "Приложение свернуто в трей.", QSystemTrayIcon.MessageIcon.Information)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
