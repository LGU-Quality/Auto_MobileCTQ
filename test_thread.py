from PyQt5.QtCore import QThread, pyqtSignal
from automation import execute_test_steps

from device_utils import get_android_device, get_ios_device

class TestThread(QThread):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str)

    def __init__(self, app_info, test_info, platform_name, wait_time, test_count):
        super().__init__()
        self.app_info = app_info
        self.test_info = test_info
        self.platform_name = platform_name
        self.wait_time = wait_time
        self.test_count = test_count

    def run(self):
        device_name = get_android_device() if self.platform_name == "Android" else get_ios_device()
        self.log_signal.emit(f"Appium 연결 시작... (디바이스: {device_name}, 플랫폼: {self.platform_name})")

        try:
            search_times, avg_time = execute_test_steps(
                self.app_info["package"],
                self.app_info["activity"],
                self.test_info,
                device_name,
                self.platform_name,
                self.wait_time,
                self.test_count,
                self.log_signal)
            
            result_message = f"🏁 평균 시간: {avg_time:.2f} 초"
            self.result_signal.emit(result_message)
            self.log_signal.emit(result_message)

        except Exception as e:
            self.result_signal.emit(f"테스트 중 오류 발생: {str(e)}")
            print(e)
        # finally:
        #     print("끝")