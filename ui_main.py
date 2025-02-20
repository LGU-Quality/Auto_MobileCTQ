import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QSpacerItem,
    QComboBox, QSpinBox, QTextEdit, QMenu, QFrame, QHBoxLayout, QCheckBox, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from test_thread import TestThread


class ClickableLabel(QLabel):
    """우클릭 복사가 가능한 QLabel"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        menu = QMenu(self)
        copy_action = menu.addAction("복사")
        action = menu.exec_(self.mapToGlobal(position))
        if action == copy_action:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text().strip())


class AutomationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTQ 측정 Tool")
        self.setGeometry(300, 200, 500, 850)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
            }
            QLabel {
                color: #EAEAEA;
                font-size: 14px;
            }
            QPushButton {
                background-color: #444444;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QComboBox, QSpinBox, QTextEdit {
                background-color: #3B3B3B;
                color: white;
                border-radius: 5px;
                padding: 6px;
                font-size: 15px;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 10px;
                padding: 10px;
                margin-top: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #D0D0D0;
            }
        """)

        self.layout = QVBoxLayout()

        # 📌 Appium 서버 정보
        self.appium_server_info = QLabel("📡 Appium 서버: 127.0.0.1:4723")
        self.appium_server_info.setFont(QFont("Arial", 14, QFont.Bold))
        self.layout.addWidget(self.appium_server_info)

        # 📱 앱 선택 그룹
        self.app_group = QGroupBox("📱 테스트 대상")
        app_layout = QVBoxLayout()

        self.app_combo = QComboBox()
        self.app_combo.currentIndexChanged.connect(self.load_tests)
        app_layout.addWidget(self.app_combo)

        self.test_combo = QComboBox()
        self.test_combo.currentIndexChanged.connect(self.update_description)
        app_layout.addWidget(self.test_combo)

        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Android", "iOS"])
        app_layout.addWidget(self.platform_combo)

        self.run_all_checkbox = QCheckBox("대상앱 내 모든 측정 항목 자동 순차 측정")
        self.run_all_checkbox.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold;")  # ✅ 밝은 색으로 변경
        app_layout.addWidget(self.run_all_checkbox)

        self.app_group.setLayout(app_layout)
        self.layout.addWidget(self.app_group)

        # 설명 라벨
        self.description_label = QLabel("-")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("border: 1px solid gray; padding: 8px; background-color: #444;")
        self.layout.addWidget(self.description_label)

        # ⚙ 테스트 설정 그룹
        self.config_group = QGroupBox("⚙ 테스트 설정")
        config_layout = QHBoxLayout()

        self.test_count_label = QLabel("🔄 반복 횟수")
        config_layout.addWidget(self.test_count_label)

        self.test_count_spin = QSpinBox()
        self.test_count_spin.setMinimum(1)
        self.test_count_spin.setMaximum(100)
        self.test_count_spin.setValue(3)
        config_layout.addWidget(self.test_count_spin)

        self.wait_time_label = QLabel("⏳ 최대 대기 시간(초)")
        config_layout.addWidget(self.wait_time_label)

        self.wait_time_spin = QSpinBox()
        self.wait_time_spin.setMinimum(1)
        self.wait_time_spin.setMaximum(30)
        self.wait_time_spin.setValue(10)
        config_layout.addWidget(self.wait_time_spin)

        self.config_group.setLayout(config_layout)
        self.layout.addWidget(self.config_group)

        # 📌 버튼 레이아웃
        self.button_layout = QHBoxLayout()

        self.run_button = QPushButton("🚀 시작")
        self.run_button.clicked.connect(self.run_test)
        self.button_layout.addWidget(self.run_button)

        self.stop_button = QPushButton("⛔ 중지")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #FF5733;")
        self.stop_button.clicked.connect(self.stop_test)
        self.button_layout.addWidget(self.stop_button)

        self.layout.addLayout(self.button_layout)

        # 📊 결과 창
        # self.result_label = QLabel("📊 결과 출력:")
        self.result_label = ClickableLabel("📊 결과 출력:")
        self.result_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold;")
        self.result_label.setWordWrap(True)
        self.layout.addWidget(self.result_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #3B3B3B; border: 1px solid #555; padding: 10px;")
        self.layout.addWidget(self.log_output)

        # 컨테이너 설정
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.load_apps()
        self.test_thread = None
        self.running_tests = []


    def add_separator(self):
        """구분선 추가"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

    def load_apps(self):
        """앱 목록 불러오기"""
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)

        # Appium 서버 정보 설정
        self.appium_host = config.get("appium_server", {}).get("host", "127.0.0.1")
        self.appium_port = config.get("appium_server", {}).get("port", 4723)
        self.appium_server_info.setText(f"📡 Appium 서버 정보: {self.appium_host}:{self.appium_port}")

        self.apps = config
        self.apps.pop("appium_server", None)

        self.app_combo.clear()
        self.app_combo.addItems(self.apps.keys())

    def load_tests(self):
        """앱 변경 시 테스트 목록 업데이트"""
        self.test_combo.clear()
        app_name = self.app_combo.currentText()
        if app_name and "tests" in self.apps[app_name]:
            self.test_combo.addItems(self.apps[app_name]["tests"].keys())
            self.update_description()

    def update_description(self):
        """테스트 설명 업데이트"""
        app_name = self.app_combo.currentText()
        test_name = self.test_combo.currentText()
        if app_name and test_name in self.apps[app_name]["tests"]:
            description = self.apps[app_name]["tests"][test_name].get("description", "설명이 없습니다.")
            self.description_label.setText(description)

    def run_test(self):
        """테스트 실행"""
        app_name = self.app_combo.currentText()
        platform_name = self.platform_combo.currentText()

        if not app_name:
            self.log_output.append("❌ 앱을 선택하세요.")
            return

        app_info = self.apps[app_name]
        test_cases = app_info.get("tests", {})

        if self.run_all_checkbox.isChecked():
            self.log_output.append(f"🔄 {app_name}의 모든 테스트 자동 실행 시작...")
            self.run_all_tests(app_info, test_cases, platform_name)
        else:
            test_name = self.test_combo.currentText()
            if not test_name:
                self.log_output.append("❌ 테스트 항목을 선택하세요.")
                return

            test_info = test_cases[test_name]
            self.run_single_test(app_info, test_name, test_info, platform_name)

    def run_single_test(self, app_info, test_name, test_info, platform_name):
        """단일 테스트 실행"""
        self.log_output.append(f"🟢 [{test_name}] 측정 시작...")
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.test_thread = TestThread(
            app_info, test_info, platform_name,
            self.wait_time_spin.value(), self.test_count_spin.value()
        )
        self.test_thread.test_name = test_name  # ✅ 실행된 테스트 이름 저장
        self.running_tests.append(self.test_thread)

        self.test_thread.log_signal.connect(self.update_log)
        self.test_thread.result_signal.connect(self.show_result)
        self.test_thread.finished.connect(self.on_test_completed)
        self.test_thread.start()

    def run_all_tests(self, app_info, test_cases, platform_name):
        """비동기 방식으로 모든 테스트 실행"""
        test_names = list(test_cases.keys())

        def run_next(index):
            if index >= len(test_names):
                self.on_test_completed()
                return

            test_name = test_names[index]
            test_info = test_cases[test_name]
            self.run_single_test(app_info, test_name, test_info, platform_name)

            self.test_thread.finished.connect(lambda: run_next(index + 1))

        run_next(0)

    def stop_test(self):
        """테스트 중단"""
        for thread in self.running_tests:
            thread.terminate()
        self.running_tests.clear()
        self.log_output.append("⛔ 테스트 중단 완료.")

    def update_log(self, message):
        """로그를 업데이트하고 자동 스크롤"""
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def show_result(self, result):
        """결과를 UI에 표시하고, 복사 가능하게 유지"""
        self.result_label.setText(result)

    def on_test_completed(self):
        """테스트 완료 후 UI 복구 및 완료 메시지 출력"""
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        if self.test_thread and self.test_thread.test_name:
            self.log_output.append(f"🏁 [{self.test_thread.test_name}] 측정이 완료됐습니다.")
        else:
            self.log_output.append("🏁 테스트가 완료되었습니다.")
