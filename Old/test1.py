# from appium import webdriver
# from appium.webdriver.common.appiumby import AppiumBy
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# # Import Appium UiAutomator2 driver for Android platforms (AppiumOptions)
# from appium.options.android import UiAutomator2Options

# # 앱의 기본 정보 설정
# desired_caps = {
#     "platformName": "Android",
#     "deviceName": "device",  # 실제 디바이스 사용 시 'adb devices'로 확인 가능
#     "appPackage": "com.lguplus.iptv3.apps.multiview",  # 테스트할 앱 패키지명
#     # "appActivity": ".MainActivity",  # 앱의 시작 액티비티
#     "automationName": "UiAutomator2",  # Android 자동화 드라이버
#     # "noReset": True,  # 앱 상태를 초기화하지 않음
#     # "newCommandTimeout": 300  # 연결 유지 시간 (초)
# }

# # Appium 서버와 연결
# driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# # 측정 시작 시간 기록
# start_time = time.time()

# try:
#     # 앱 실행 (자동 실행될 경우 생략 가능)
#     driver.launch_app()

#     # 특정 UI 요소가 로드될 때까지 대기 (최대 20초)
#     wait = WebDriverWait(driver, 20)
#     element = wait.until(
#         EC.presence_of_element_located((AppiumBy.ID, "com.example.app:id/someElement"))
#     )

#     # 측정 완료 시간 기록
#     end_time = time.time()

#     # 실행 시간 계산
#     launch_time = end_time - start_time
#     print(f"App launch time: {launch_time:.2f} seconds")

# except Exception as e:
#     print(f"Error during app launch: {e}")

# finally:
#     # 테스트 완료 후 드라이버 종료
#     driver.quit()


# import unittest
# from appium import webdriver
# from appium.webdriver.common.appiumby import AppiumBy

# # Import Appium UiAutomator2 driver for Android platforms (AppiumOptions)
# from appium.options.android import UiAutomator2Options

# capabilities = dict(
#     platformName='Android',
#     automationName='uiautomator2',
#     deviceName='device',
#     appPackage='com.android.settings',
#     appActivity='.Settings',
# )

# appium_server_url = 'http://localhost:4723'

# # Converts capabilities to AppiumOptions instance
# capabilities_options = UiAutomator2Options().load_capabilities(capabilities)

# class TestAppium(unittest.TestCase):
#     def setUp(self) -> None:
#         self.driver = webdriver.Remote(command_executor=appium_server_url,options=capabilities_options)

#     def tearDown(self) -> None:
#         if self.driver:
#             self.driver.quit()

#     def test_find_battery(self) -> None:
#         el = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Battery"]')
#         el.click()

# if __name__ == '__main__':
#     unittest.main()


import unittest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options

# 테스트할 디바이스 및 앱의 설정
capabilities = {
    "platformName": "Android",
    "automationName": "uiautomator2",
    "deviceName": "192.168.219.104:5555",  # 실제 디바이스의 adb id 확인 필요
    "appPackage": "com.android.settings",  # 테스트할 앱 패키지명
    "appActivity": ".Settings",  # 앱의 시작 액티비티
    "noReset": True,  # 앱의 이전 상태 유지
    "newCommandTimeout": 300  # 명령 타임아웃 설정 (초)
}

# Appium 서버 URL
appium_server_url = 'http://localhost:4723'

# 옵션 인스턴스 생성
capabilities_options = UiAutomator2Options().load_capabilities(capabilities)

class TestAndroidSettings(unittest.TestCase):
    def setUp(self):
        """Appium 서버에 연결하여 드라이버 생성"""
        self.driver = webdriver.Remote(command_executor=appium_server_url, options=capabilities_options)

    def tearDown(self):
        """테스트 종료 후 드라이버 종료"""
        if self.driver:
            self.driver.quit()

    def test_find_battery_settings(self):
        """설정 앱에서 'Battery' 옵션을 찾고 클릭하는 테스트"""
        try:
            # 'Battery' 텍스트를 가진 요소 검색 및 클릭
            el = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Battery"]')
            el.click()

            # 클릭 후 'Battery' 화면으로 정상 진입 확인
            assert "Battery" in self.driver.page_source, "Battery screen did not open."
            print("Battery option clicked successfully.")

        except Exception as e:
            self.fail(f"Test failed due to: {e}")

if __name__ == '__main__':
    unittest.main()
