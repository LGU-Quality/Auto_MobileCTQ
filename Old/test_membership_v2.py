import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from statistics import mean
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Appium 서버 URL 및 디바이스 설정
APPIUM_SERVER_URL = "http://127.0.0.1:4723"

DESIRED_CAPABILITIES = {
	"platformName": "Android",
	"appium:automationName": "uiautomator2",
	"appium:deviceName": "R3CX200EY4K",
	"appium:appPackage": "uplus.membership",
	"appium:appActivity": "com.uplus.membership.smart.ui.main.MainActivity",
	"appium:noReset": True,
	"appium:fullReset": False,
}

# 테스트 실행 횟수
TEST_COUNT = 10
launch_times = []

def measure_app_launch_time():
    """앱 실행 시간을 측정하는 함수"""
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=UiAutomator2Options().load_capabilities(DESIRED_CAPABILITIES))

    try:
        for i in range(TEST_COUNT):
            print(f"테스트 {i + 1}/{TEST_COUNT} 시작...")

            # 앱 강제 종료
            driver.terminate_app(DESIRED_CAPABILITIES["appium:appPackage"])
            time.sleep(2)  # 앱 종료 대기

            # 실행 시간 측정 시작
            start_time = time.time()

            # 앱 실행
            driver.activate_app(DESIRED_CAPABILITIES["appium:appPackage"])

            # 특정 UI 요소가 나타날 때까지 대기 _ 암묵적 대기
            # driver.implicitly_wait(10)  # 최대 10초 대기
            # element = driver.find_element("xpath", "//android.widget.Image[@text='placeholder'][1]")

            # 특정 요소가 나타날 때까지 최대 10초 기다림 _ 명시적 대기
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//android.widget.Image[@text='placeholder'][1]"))
            )

            end_time = time.time()

            launch_time = end_time - start_time
            launch_times.append(launch_time)
            print(f"실행 시간: {launch_time:.2f} 초")

            # 앱 종료 후 대기
            time.sleep(3)

    finally:
        driver.quit()


# 테스트 실행
measure_app_launch_time()

# 결과 분석 및 출력
average_time = mean(launch_times)
print(f"\n앱 실행 속도 측정 완료. 평균 실행 시간: {average_time:.2f} 초")

# 결과 저장
with open("app_launch_times.txt", "w") as file:
    file.write("앱 실행 속도 측정 결과 (초):\n")
    for idx, time_value in enumerate(launch_times, 1):
        file.write(f"시도 {idx}: {time_value:.2f} 초\n")
    file.write(f"\n평균 실행 시간: {average_time:.2f} 초\n")

print("결과가 'app_launch_times.txt'에 저장되었습니다.")
