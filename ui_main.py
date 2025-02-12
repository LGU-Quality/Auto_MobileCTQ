import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QComboBox, QSpinBox, QTextEdit, QMenu, QFrame
from PyQt5.QtCore import Qt
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
            clipboard.setText(self.text().strip())  # HTML 포맷 제거 후 복사


class AutomationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTQ 측정 Tool")
        self.setGeometry(300, 200, 600, 800)

        self.layout = QVBoxLayout()

        # 📌 앱 선택
        self.label = QLabel("테스트할 앱을 선택하세요:")
        self.layout.addWidget(self.label)

        self.app_combo = QComboBox()
        self.app_combo.currentIndexChanged.connect(self.load_tests)
        self.layout.addWidget(self.app_combo)

        # 📌 측정 항목 선택
        self.test_label = QLabel("측정할 항목을 선택하세요:")
        self.layout.addWidget(self.test_label)

        self.test_combo = QComboBox()
        self.test_combo.currentIndexChanged.connect(self.update_description)
        self.layout.addWidget(self.test_combo)

        # 📌 구분선 추가 (설명 위)
        self.line1 = QFrame()
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.line1)

        # 📌 측정 항목 설명 표시
        self.description_label = QLabel("-")
        self.description_label.setWordWrap(True)
        self.layout.addWidget(self.description_label)

        # 📌 구분선 추가 (설명 아래)
        self.line2 = QFrame()
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.line2)

        # 📌 플랫폼 선택
        self.platform_label = QLabel("테스트할 플랫폼 선택:")
        self.layout.addWidget(self.platform_label)

        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Android", "iOS"])
        self.layout.addWidget(self.platform_combo)

        # 📌 테스트 횟수 설정
        self.test_count_label = QLabel("테스트 횟수 설정:")
        self.layout.addWidget(self.test_count_label)

        self.test_count_spin = QSpinBox()
        self.test_count_spin.setMinimum(1)
        self.test_count_spin.setMaximum(100)
        self.test_count_spin.setValue(3)
        self.layout.addWidget(self.test_count_spin)

        # 📌 대기 시간 설정
        self.wait_time_label = QLabel("터치 후 최대 대기 시간(초):")
        self.layout.addWidget(self.wait_time_label)

        self.wait_time_spin = QSpinBox()
        self.wait_time_spin.setMinimum(1)
        self.wait_time_spin.setMaximum(30)
        self.wait_time_spin.setValue(10)
        self.layout.addWidget(self.wait_time_spin)

        # 📌 테스트 실행 버튼
        self.run_button = QPushButton("테스트 실행")
        self.run_button.clicked.connect(self.run_test)
        self.layout.addWidget(self.run_button)

        # 📌 결과 출력
        self.result_label = ClickableLabel("결과 출력:")
        self.result_label.setWordWrap(True)
        self.layout.addWidget(self.result_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setLineWrapMode(QTextEdit.WidgetWidth)
        self.layout.addWidget(self.log_output)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.load_apps()

    def load_apps(self):
        """앱 목록을 불러와 UI에 반영"""
        with open("config.json", "r", encoding="utf-8") as file:
            self.apps = json.load(file)

        self.app_combo.clear()  # 기존 목록 초기화
        self.app_combo.addItems(self.apps.keys())

    def load_tests(self):
        """앱이 변경될 때 해당 앱의 측정 항목을 로드"""
        self.test_combo.clear()
        app_name = self.app_combo.currentText()

        if app_name and app_name in self.apps:
            self.test_combo.addItems(self.apps[app_name]["tests"].keys())
            self.update_description()  # 기본적으로 첫 번째 항목 설명 표시
        else:
            self.description_label.setText("설명: -")  # 항목이 없을 경우 초기화

    def update_description(self):
        """사용자가 선택한 테스트 항목의 설명을 업데이트"""
        app_name = self.app_combo.currentText()
        test_name = self.test_combo.currentText()

        if app_name and test_name and app_name in self.apps:
            description = self.apps[app_name]["tests"].get(test_name, {}).get("description", "설명이 없습니다.")
            self.description_label.setText(f"{description}")
        else:
            self.description_label.setText("설명: -")

    def run_test(self):
        """테스트 실행"""
        app_name = self.app_combo.currentText()
        test_name = self.test_combo.currentText()
        platform_name = self.platform_combo.currentText()
        print(f"🔍 platform_name 확인: {platform_name}")

        if not app_name or not test_name:
            self.log_output.append("앱 또는 테스트 정보를 찾을 수 없습니다.")
            self.result_label.setText("❌ 테스트 실패: 앱 또는 테스트 정보 없음") 
            return

        app_info = self.apps[app_name]
        test_info = app_info["tests"][test_name]

        # ✅ 로그 추가 (test_info 구조 확인)
        print(f"🔍 test_info 구조 확인: {test_info}")

        self.log_output.append(f"🟢{app_name}앱의 [{test_name}] 측정 시작...")

        self.run_button.setEnabled(False)
        self.test_thread = TestThread(
            app_info,
            test_info,
            platform_name,
            self.wait_time_spin.value(),
            self.test_count_spin.value()
        )
        self.test_thread.log_signal.connect(self.update_log)
        self.test_thread.result_signal.connect(self.show_result)
        self.test_thread.finished.connect(self.on_test_completed)
        self.test_thread.start()


    def update_log(self, message):
        """로그를 업데이트하고 자동 스크롤"""
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def show_result(self, result):
        """결과를 UI에 표시하고, 복사 가능하게 유지"""
        self.result_label.setText(result)

    def on_test_completed(self):
        """테스트 완료 후 UI 복구"""
        self.run_button.setEnabled(True)
        self.log_output.append("🏁 테스트가 완료되었습니다.")