# adb shell dumpsys window | Select-String -Pattern "mCurrentFocus" 파워셀 에서 현재 포커스위치의 앱/액티비티 반환
# mCurrentFocus=Window{5d4306 u0 uplus.membership/com.uplus.membership.smart.ui.main.MainActivity}
# mCurrentFocus=Window{713d311 u0 lgt.call/lgt.call.Main}
# com.nhn.android.nmap/com.naver.map.LaunchActivity
# Find By	Selector
# -android uiautomator
# (docs)
# new UiSelector().text("placeholder").instance(0)
# xpath
# (//android.widget.Image[@text="placeholder"])[1]

import unittest, time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy

capabilities = {
	"platformName": "Android",
	"appium:automationName": "uiautomator2",
	"appium:deviceName": "R3CX200EY4K",
	"appium:appPackage": "uplus.membership",
	"appium:appActivity": "com.uplus.membership.smart.ui.main.MainActivity",
	"appium:noReset": True,
	"appium:fullReset": False,
	"appium:newCommandTimeout": 3600,
}

appium_server_url = 'http://localhost:4723'

class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        # Appium 드라이버 초기화
        self.driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))


    def tearDown(self) -> None:
        # 테스트 종료 시 드라이버 종료
        if self.driver:
            self.driver.quit()

    def test_launch_time(self):
        # 앱 실행 시작 시간 기록
        start_time = time.time()

        # 앱 실행 후 "U+멤버십" 텍스트가 있는지 확인
        try:
            # element = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="홈"]')
            # element = self.driver.find_element(by=AppiumBy.ID, value="com.uplus.membership:id/home_button")
            # element = self.driver.find_element(
            #     by=AppiumBy.ANDROID_UIAUTOMATOR,
            #     value='new UiSelector().text("U+모바일매니저").instance(0)'
            # )
            element = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Image[@text="placeholder"]')
            # 요소가 발견되면 성공
            print(f"'U+모바일매니저' 텍스트 발견: {element.text}")
        except Exception as e:
            self.fail(f"'U+모바일매니저' 텍스트가 발견되지 않았습니다: {e}")

        # 첫 화면 로드 완료 시간 기록
        end_time = time.time()

        # 소요 시간 계산
        launch_time = end_time - start_time
        print(f"앱 실행 후 첫 화면까지 소요 시간: {launch_time:.2f}초")
            
        
if __name__ == '__main__':
    unittest.main()