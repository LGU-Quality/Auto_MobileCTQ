from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions  # iOS 지원 추가
import time
from statistics import mean
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.appiumby import AppiumBy

APPIUM_SERVER_URL = "http://127.0.0.1:4723"


def setup_driver(platform_name, app_package, app_activity, device_name):
    """Appium 드라이버 설정"""
    options = UiAutomator2Options() if platform_name == "Android" else XCUITestOptions()
    options.platform_name = platform_name
    options.device_name = device_name
    options.app_package = app_package if platform_name == "Android" else None
    options.app_activity = app_activity if platform_name == "Android" else None
    options.automation_name = "UiAutomator2" if platform_name == "Android" else "XCUITest"
    options.no_reset = True
    return webdriver.Remote(APPIUM_SERVER_URL, options=options)


def get_locator_strategy(element_info, platform_name):
    """ 요소 정보에서 locator_strategy와 value를 추출하고, 기본값을 적용 """
    
    if not element_info:
        raise ValueError("❌ 유효하지 않은 요소 정보!")

    platform_key = platform_name.lower()

    # 기본적으로 XPATH를 사용하도록 설정
    default_strategy = By.XPATH
    strategy_mapping = {
        "ID": By.ID,
        "XPATH": By.XPATH,
        "ANDROID_UIAUTOMATOR": AppiumBy.ANDROID_UIAUTOMATOR,
        "IOS_PREDICATE": AppiumBy.IOS_PREDICATE,
        "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID
    }

    # ✅ 키 존재 여부 확인 후 기본값 적용
    locator_strategy = element_info.get("locator_strategy", {}).get(platform_key, "XPATH")
    locator_value = element_info.get("value", {}).get(platform_key, None)

    if not locator_value:
        raise ValueError(f"❌ '{platform_key}'에 대한 locator 값이 없습니다!")

    return strategy_mapping.get(locator_strategy, default_strategy), locator_value



def measure_app_launch_time(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """앱 실행 후 특정 UI가 나타날 때까지의 시간을 측정"""
    
    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    launch_times = []

    try:
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2)
            driver.activate_app(app_package)
            start_time = time.time()

            # ✅ 요소 탐색 전략 결정
            by_strategy, success_element = get_locator_strategy(test_info["success_element"], platform_name)

            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((by_strategy, success_element))
                )
            except TimeoutException:
                log_signal.emit(f"❌ 요소 탐색 실패 ({by_strategy}): {success_element}")
                continue

            end_time = time.time()
            launch_time = end_time - start_time
            launch_times.append(launch_time)

            log_signal.emit(f"✅ 실행 시간: {launch_time:.2f} 초")

            time.sleep(3)

    except Exception as e:
        print(e)

    finally:
        driver.quit()

    avg_time = sum(launch_times) / len(launch_times) if launch_times else 0
    return launch_times, avg_time


def measure_screen_transition(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """특정 화면(A)에서 화면(B)으로 이동하는 데 걸리는 시간을 측정"""

    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    transition_times = []

    try:
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2)
            driver.activate_app(app_package)

            start_by, start_element = get_locator_strategy(test_info["start_element"], platform_name)
            action_by, action_element = get_locator_strategy(test_info["action"], platform_name)
            end_by, end_element = get_locator_strategy(test_info["end_element"], platform_name)

            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((start_by, start_element))
                )
            except TimeoutException:
                log_signal.emit("❌ 시작 화면 탐색 실패")
                continue

            try:
                action_elem = driver.find_element(action_by, action_element)
                action_elem.click()
                log_signal.emit("✅ 버튼 클릭 완료, 화면 전환 시작")
            except:
                log_signal.emit("❌ 버튼을 찾을 수 없음")
                continue

            start_time = time.time()

            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((end_by, end_element))
                )
                end_time = time.time()
                transition_time = end_time - start_time
                transition_times.append(transition_time)
                log_signal.emit(f"✅ 화면 전환 완료: {transition_time:.2f} 초")
            except TimeoutException:
                log_signal.emit("❌ 화면 전환 실패")

            time.sleep(3)

    finally:
        driver.quit()

    avg_time = sum(transition_times) / len(transition_times) if transition_times else 0
    return transition_times, avg_time


def measure_search_time(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """검색어 입력 후 검색 결과가 나타날 때까지의 시간을 측정"""

    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    search_times = []

    try:
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2)
            driver.activate_app(app_package)

            start_by, start_element = get_locator_strategy(test_info["start_element"], platform_name)
            input_by, input_element = get_locator_strategy(test_info["input_field"], platform_name)
            search_by, search_element = get_locator_strategy(test_info["search_button"], platform_name)
            end_by, end_element = get_locator_strategy(test_info["end_element"], platform_name)

            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((start_by, start_element))
            )

            search_input = driver.find_element(input_by, input_element)
            search_input.clear()
            search_input.send_keys(test_info["search_text"])

            search_button = driver.find_element(search_by, search_element)
            start_time = time.time()
            search_button.click()

            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((end_by, end_element))
            )
            end_time = time.time()

            search_time = end_time - start_time
            search_times.append(search_time)

            log_signal.emit(f"✅ 검색 완료 시간: {search_time:.2f} 초")

            time.sleep(3)

    finally:
        driver.quit()

    avg_time = sum(search_times) / len(search_times) if search_times else 0
    return search_times, avg_time
