#!/usr/bin/env python3
# Copyright 2025 Vyacheslav Nuykin. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import yaml
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLineEdit, QPushButton, QTextEdit, QLabel,
    QGroupBox, QComboBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QFont


class DatabaseLauncherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐘 Docker Database Launcher (Enterprise)")
        self.resize(900, 650)
        self.process = None
        self.profile_dir = Path.home() / ".docker-db" / "profiles"
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Profile management bar
        profile_layout = QHBoxLayout()
        profile_label = QLabel("Profile:")
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(200)
        self.load_profile_btn = QPushButton("📂 Load")
        self.save_profile_btn = QPushButton("💾 Save As")
        self.refresh_profiles()
        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(self.profile_combo)
        profile_layout.addWidget(self.load_profile_btn)
        profile_layout.addWidget(self.save_profile_btn)
        profile_layout.addStretch()
        main_layout.addLayout(profile_layout)

        # Database tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_postgres_tab(), "PostgreSQL")
        self.tabs.addTab(self.create_mysql_tab(), "MySQL")
        self.tabs.addTab(self.create_redis_tab(), "Redis")
        self.tabs.addTab(self.create_mongo_tab(), "MongoDB")
        self.tabs.addTab(self.create_custom_tab(), "Custom")
        main_layout.addWidget(self.tabs)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.launch_btn = QPushButton("🚀 Launch")
        self.stop_btn = QPushButton("🛑 Stop")
        self.clear_btn = QPushButton("🧹 Clear Log")
        btn_layout.addWidget(self.launch_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.clear_btn)
        main_layout.addLayout(btn_layout)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        main_layout.addWidget(self.log_output)

        # Signals
        self.launch_btn.clicked.connect(self.launch_container)
        self.stop_btn.clicked.connect(self.stop_container)
        self.clear_btn.clicked.connect(self.log_output.clear)
        self.load_profile_btn.clicked.connect(self.load_selected_profile)
        self.save_profile_btn.clicked.connect(self.save_current_as_profile)
        self.profile_combo.currentTextChanged.connect(self.on_profile_selected)

        self.apply_dark_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #1e1e1e; color: #d4d4d4; }
            QLineEdit, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                color: #cccccc;
                padding: 4px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1565c0; }
            QTabWidget::pane { border: 1px solid #3c3c3c; }
            QTabBar::tab {
                background: #2d2d2d;
                color: #cccccc;
                padding: 8px 12px;
            }
            QTabBar::tab:selected {
                background: #0d47a1;
                color: white;
            }
            QLabel { color: #aaaaaa; }
            QComboBox {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                padding: 4px;
            }
        """)

    def create_input_group(self, fields):
        group = QGroupBox()
        layout = QVBoxLayout()
        widgets = {}
        for label_text, key in fields:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(120)
            input_field = QLineEdit()
            row.addWidget(label)
            row.addWidget(input_field)
            layout.addLayout(row)
            widgets[key] = input_field
        group.setLayout(layout)
        return group, widgets

    def create_postgres_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        fields = [
            ("Container Name:", "name"),
            ("User:", "user"),
            ("Password:", "password"),
            ("Database:", "db"),
            ("Host Port:", "port"),
            ("Image (opt):", "image"),
        ]
        self.pg_group, self.pg_inputs = self.create_input_group(fields)
        self.pg_inputs["image"].setText("postgres:16")
        self.pg_inputs["port"].setText("5432")
        layout.addWidget(self.pg_group)
        layout.addStretch()
        return widget

    def create_mysql_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        fields = [
            ("Container Name:", "name"),
            ("User:", "user"),
            ("Password:", "password"),
            ("Database:", "db"),
            ("Host Port:", "port"),
            ("Image (opt):", "image"),
        ]
        self.mysql_group, self.mysql_inputs = self.create_input_group(fields)
        self.mysql_inputs["image"].setText("mysql:8")
        self.mysql_inputs["port"].setText("3306")
        layout.addWidget(self.mysql_group)
        layout.addStretch()
        return widget

    def create_redis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        fields = [
            ("Container Name:", "name"),
            ("Host Port:", "port"),
            ("Image (opt):", "image"),
        ]
        self.redis_group, self.redis_inputs = self.create_input_group(fields)
        self.redis_inputs["image"].setText("redis:7")
        self.redis_inputs["port"].setText("6379")
        layout.addWidget(self.redis_group)
        layout.addStretch()
        return widget

    def create_mongo_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        fields = [
            ("Container Name:", "name"),
            ("User:", "user"),
            ("Password:", "password"),
            ("Database:", "db"),
            ("Host Port:", "port"),
            ("Image (opt):", "image"),
        ]
        self.mongo_group, self.mongo_inputs = self.create_input_group(fields)
        self.mongo_inputs["image"].setText("mongo:7")
        self.mongo_inputs["port"].setText("27017")
        layout.addWidget(self.mongo_group)
        layout.addStretch()
        return widget

    def create_custom_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        fields = [
            ("Container Name:", "name"),
            ("Image:", "image"),
            ("Host Port (opt):", "port"),
            ("Env Vars (opt):", "env"),
        ]
        self.custom_group, self.custom_inputs = self.create_input_group(fields)
        layout.addWidget(self.custom_group)
        layout.addStretch()
        return widget

    def get_current_inputs(self):
        current = self.tabs.currentIndex()
        mapping = {
            0: ("postgres", self.pg_inputs),
            1: ("mysql", self.mysql_inputs),
            2: ("redis", self.redis_inputs),
            3: ("mongo", self.mongo_inputs),
            4: ("custom", self.custom_inputs),
        }
        return mapping.get(current, (None, {}))

    def refresh_profiles(self):
        self.profile_combo.clear()
        for f in self.profile_dir.glob("*.yaml"):
            self.profile_combo.addItem(f.stem)

    def on_profile_selected(self, name):
        if not name:
            return
        profile_path = self.profile_dir / f"{name}.yaml"
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self.load_config_into_ui(config)
        except Exception as e:
            self.log_output.append(f"❌ Failed to load profile: {e}")

    def load_selected_profile(self):
        name = self.profile_combo.currentText()
        if name:
            self.on_profile_selected(name)

    def save_current_as_profile(self):
        name, ok = QFileDialog.getSaveFileName(
            self, "Save Profile", str(self.profile_dir), "YAML Files (*.yaml)"
        )
        if not ok or not name:
            return
        if not name.endswith(".yaml"):
            name += ".yaml"
        config = self.get_config_from_ui()
        try:
            with open(name, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            self.refresh_profiles()
            self.log_output.append(f"✅ Profile saved: {Path(name).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save profile:\n{e}")

    def get_config_from_ui(self):
        db_type, inputs = self.get_current_inputs()
        if not db_type:
            return {}
        config = {"type": db_type}
        for key, widget in inputs.items():
            value = widget.text().strip()
            if value:
                config[key] = value
        return config

    def load_config_into_ui(self, config):
        db_type = config.get("type")
        tab_index = {
            "postgres": 0,
            "mysql": 1,
            "redis": 2,
            "mongo": 3,
            "custom": 4,
        }.get(db_type, 0)
        self.tabs.setCurrentIndex(tab_index)

        inputs_map = {
            0: self.pg_inputs,
            1: self.mysql_inputs,
            2: self.redis_inputs,
            3: self.mongo_inputs,
            4: self.custom_inputs,
        }
        inputs = inputs_map.get(tab_index, {})
        for key, widget in inputs.items():
            widget.setText(str(config.get(key, "")))

    def launch_container(self):
        db_type, inputs = self.get_current_inputs()
        if not db_type:
            return

        args = [sys.executable, str(Path(__file__).parent / "core.py"), db_type]
        valid = True

        for key, widget in inputs.items():
            value = widget.text().strip()
            if key in ("name", "user", "password", "db", "image") and not value:
                if not (db_type == "custom" and key in ("user", "password", "db")):
                    self.log_output.append(f"❌ Field '{key}' is required.")
                    valid = False
            if value:
                if key == "env":
                    env_vars = value.split()
                    for env in env_vars:
                        args.extend(["--env", env])
                else:
                    args.extend([f"--{key}", value])

        if not valid:
            return

        self.log_output.append(f"📦 Launching: {' '.join(args)}")
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.start(args[0], args[1:])

    def stop_container(self):
        db_type, inputs = self.get_current_inputs()
        name_widget = inputs.get("name")
        if not name_widget or not name_widget.text().strip():
            self.log_output.append("❌ Container name is required to stop.")
            return

        name_val = name_widget.text().strip()
        args = [sys.executable, str(Path(__file__).parent / "core.py"), "stop", "--name", name_val]
        self.log_output.append(f"🛑 Stopping: {' '.join(args)}")
        subprocess.run(args, capture_output=True, text=True)

    def handle_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode(errors='ignore')
            if data.strip():
                self.log_output.append(data.strip())

    def handle_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode(errors='ignore')
            if data.strip():
                self.log_output.append(f"❌ {data.strip()}")

    def process_finished(self):
        self.log_output.append("✅ Command finished.")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DatabaseLauncherGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
