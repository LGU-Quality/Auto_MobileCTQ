# adb shell dumpsys window | Select-String -Pattern "mCurrentFocus" 파워셀 에서 현재 포커스위치의 앱/액티비티 반환
# mCurrentFocus=Window{eaba39d u0 com.lguplus.iptv3.base.launcher/com.lguplus.iptv3.base.launcher.MainHomeActivity}

import unittest, time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

# capabilities = {
#     "platformName": "Android",
#     "automationName": "uiautomator2",
#     "deviceName": "192.168.219.104:5555",  # 실제 디바이스의 adb id 확인 필요
#     "appPackage": "com.lguplus.iptv3.base.launcher",  # 테스트할 앱 패키지명
#     "appActivity": ".MainHomeActivity",  # 앱의 시작 액티비티
#     "noReset": True,  # 앱의 이전 상태 유지
#     "newCommandTimeout": 10  # 명령 타임아웃 설정 (초)
# }

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='192.168.219.104:5555',
    appPackage='com.android.settings',
    appActivity='.Settings',
    noReset='true'
)

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='R3CX200EY4K',
    appPackage='com.android.settings',
    appActivity='.Settings'
)

appium_server_url = 'http://localhost:4723'

class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_find_settings(self) -> None:
        el = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="연결"]')
        el.click()
        time.sleep(2)

if __name__ == '__main__':
    unittest.main()