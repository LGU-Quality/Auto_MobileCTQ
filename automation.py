from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions  # iOS 지원 추가
import time
from statistics import mean
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

APPIUM_SERVER_URL = "http://127.0.0.1:4723"

def measure_app_launch_time(app_package, app_activity, success_xpath, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """앱 실행 후 특정 UI가 나타날 때까지의 시간을 측정"""
    success_xpath = validate_xpath(success_xpath)  # ✅ XPath 검증 추가

    options = UiAutomator2Options() if platform_name == "Android" else XCUITestOptions()
    options.platform_name = platform_name
    options.device_name = device_name
    options.app_package = app_package if platform_name == "Android" else None
    options.app_activity = app_activity if platform_name == "Android" else None
    options.automation_name = "UiAutomator2" if platform_name == "Android" else "XCUITest"
    options.no_reset = True

    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    launch_times = []

    try:
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2)

            start_time = time.time()
            driver.activate_app(app_package)

            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, success_xpath))
                )
                end_time = time.time()
                launch_time = end_time - start_time
                launch_times.append(launch_time)

                log_signal.emit(f"실행 시간: {launch_time:.2f} 초")

            except TimeoutException:
                log_signal.emit(f"오류: {wait_time}초 내에 대상 UI 요소를 찾을 수 없습니다.")
                launch_times.append(None)

            time.sleep(3)

    finally:
        driver.quit()

    avg_time = mean([t for t in launch_times if t is not None]) if launch_times else 0
    return launch_times, avg_time


def measure_screen_transition(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """특정 화면(A)에서 화면(B)으로 이동하는 데 걸리는 시간을 측정"""
    start_xpath = validate_xpath(test_info["start_element"][platform_name.lower()])
    action_xpath = validate_xpath(test_info["action"][platform_name.lower()])
    end_xpath = validate_xpath(test_info["end_element"][platform_name.lower()])

    options = UiAutomator2Options() if platform_name == "Android" else XCUITestOptions()
    options.platform_name = platform_name
    options.device_name = device_name
    options.app_package = app_package if platform_name == "Android" else None
    options.app_activity = app_activity if platform_name == "Android" else None
    options.automation_name = "UiAutomator2" if platform_name == "Android" else "XCUITest"
    options.no_reset = True

    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    transition_times = []

    try:
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2)
            driver.activate_app(app_package)

            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, start_xpath))
                )
            except TimeoutException:
                log_signal.emit("오류: A 화면이 로드되지 않았습니다.")
                transition_times.append(None)
                continue

            try:
                action_element = driver.find_element(By.XPATH, action_xpath)
                action_element.click()
                log_signal.emit("버튼 클릭 완료, 화면 전환 시작")
            except Exception:
                log_signal.emit("오류: 액션 요소를 찾을 수 없습니다.")
                transition_times.append(None)
                continue

            start_time = time.time()
            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, end_xpath))
                )
                end_time = time.time()
                transition_time = end_time - start_time
                transition_times.append(transition_time)

                log_signal.emit(f"화면 이동 시간: {transition_time:.2f} 초")

            except TimeoutException:
                log_signal.emit("오류: B 화면이 로드되지 않았습니다.")
                transition_times.append(None)

            time.sleep(3)

    finally:
        driver.quit()

    avg_time = mean([t for t in transition_times if t is not None]) if transition_times else 0
    return transition_times, avg_time



def validate_xpath(xpath):
    """XPath 값이 유효한지 검사"""
    if not xpath or not isinstance(xpath, str):
        raise ValueError(f"잘못된 XPath 값: {xpath}")
    if ";" in xpath:  # or "TBD" in xpath:
        raise ValueError(f"XPath에 잘못된 문자가 포함됨: {xpath}")
    return xpath
