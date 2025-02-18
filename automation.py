import logging
import time
import os
import json
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions  # iOS 지원 추가
from statistics import mean
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.appiumby import AppiumBy

# APPIUM_SERVER_URL = "http://127.0.0.1:4723"

# 로깅 설정
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ✅ Locator 전략 매핑
LOCATOR_MAPPING = {
    # "ID": By.ID,
    "ID": AppiumBy.ID,
    "XPATH": By.XPATH,
    "ANDROID_UIAUTOMATOR": AppiumBy.ANDROID_UIAUTOMATOR,
    "IOS_PREDICATE": AppiumBy.IOS_PREDICATE,
    "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID,
    "CLASS_NAME" : By.CLASS_NAME,
    "DOM": "DOM"
}


def load_config():
    """config.json을 로드하여 설정 값을 가져옴"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    return config

config = load_config()


def quick_search(driver, xml_string, timeout=10, poll_interval=0.05):
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 현재 페이지의 XML 소스 가져오기
        page_source = driver.page_source
        if xml_string in page_source:
            return True
        time.sleep(poll_interval)
    return False


def setup_driver(platform_name, app_package, app_activity, device_name):
    """Appium 드라이버 설정 (config.json의 포트 반영)"""
    
    # 🔥 Appium 서버 포트 설정 (기본값: 4723, config.json에서 변경 가능)
    appium_host = config.get("appium_server", {}).get("host", "127.0.0.1")
    appium_port = config.get("appium_server", {}).get("port", 4723)
    # appium_server_url = f"http://{appium_host}:{appium_port}/wd/hub"
    appium_server_url = f"http://{appium_host}:{appium_port}"

    print(f"🚀 Appium 서버 연결: {appium_server_url}")

    if platform_name.lower() == "android":
        options = UiAutomator2Options()
        options.platform_name = platform_name
        options.device_name = device_name
        options.app_package = app_package
        options.app_activity = app_activity
        options.automation_name = "UiAutomator2"
        options.no_reset = True
    else:
        options = XCUITestOptions()
        options.platform_name = platform_name
        options.device_name = device_name
        options.bundle_id = app_package
        options.automation_name = "XCUITest"
        options.no_reset = True

    driver = webdriver.Remote(appium_server_url, options=options)
    return driver


def get_locator_strategy(element_info, platform_name):
    """
    요소 정보에서 locator_strategy와 value를 추출하고 기본값을 설정
    """
    platform_key = platform_name.lower()
    default_strategy = By.XPATH  # 기본값을 XPATH로 설정

    if not element_info:
        raise ValueError("❌ 요소 정보가 유효하지 않습니다.")

    locator_strategy = element_info.get("locator_strategy", {}).get(platform_key, "XPATH")
    locator_value = element_info.get("value", {}).get(platform_key, None)

    if not locator_value:
        raise ValueError(f"❌ '{platform_key}'에 대한 locator 값이 없습니다!")

    return LOCATOR_MAPPING.get(locator_strategy, default_strategy), locator_value


""" measure_app_launch_time
- 앱 실행 시간 속도 측정 함수
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. success_element 가 탐색되는 즉시 종료
"""
def measure_app_launch_time(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """앱 실행 후 특정 UI가 나타날 때까지의 시간을 측정"""
    
    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    driver.implicitly_wait(0)  # Explicit wait만 사용하여 대기 시간 최적화

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

            if by_strategy == "DOM":
                element_found = quick_search(driver, success_element, timeout=wait_time, poll_interval=0.05)
                if not element_found: log_signal.emit(f"❌ 요소 탐색 실패")
            else:
                try:
                    WebDriverWait(driver, wait_time, poll_frequency=0.03).until(
                        EC.presence_of_element_located((by_strategy, success_element))
                    )
                except TimeoutException:
                    log_signal.emit(f"❌ 요소 탐색 실패 ({by_strategy}): {success_element}")
                    continue

            end_time = time.time()
            launch_time = end_time - start_time
            launch_times.append(launch_time)

            log_signal.emit(f"✅ 실행 시간: {launch_time:.2f} 초")

            try:
                end_button_by, end_button_element = get_locator_strategy(test_info["end_button"], platform_name)
                action_elem = driver.find_element(end_button_by, end_button_element)
                action_elem.click()
            except Exception as e:
                log_signal.emit("⚠️ 마지막 요소 클릭 실패(혹은 미설정)")

            time.sleep(1)

    except Exception as e:
        print(e)

    finally:
        driver.quit()

    avg_time = sum(launch_times) / len(launch_times) if launch_times else 0
    return launch_times, avg_time


""" measure_screen_transition
- 화면 이동 시간 측정 함수
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. start_element 대기
2. action 클릭
3. end_element 가 확인되면 종료
4. [옵션] end_button이 정의되어 있을 경우 end_button 누르고 종료
"""
def measure_screen_transition(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """특정 화면(A)에서 화면(B)으로 이동하는 데 걸리는 시간을 측정"""

    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    driver.implicitly_wait(0)  # Explicit wait만 사용하여 대기 시간 최적화

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
                WebDriverWait(driver, wait_time, poll_frequency=0.1).until(
                    EC.presence_of_element_located((end_by, end_element))
                )
                end_time = time.time()
                transition_time = end_time - start_time
                transition_times.append(transition_time)
                log_signal.emit(f"✅ 화면 전환 완료: {transition_time:.2f} 초")
            except TimeoutException:
                log_signal.emit("❌ 화면 전환 실패")

            try:
                end_button_by, end_button_element = get_locator_strategy(test_info["end_button"], platform_name)
                action_elem = driver.find_element(end_button_by, end_button_element)
                action_elem.click()
            except Exception as e:
                log_signal.emit("⚠️ 마지막 요소 클릭 실패(혹은 미설정)")

            time.sleep(1)

    finally:
        driver.quit()

    avg_time = sum(transition_times) / len(transition_times) if transition_times else 0
    return transition_times, avg_time


""" measure_screen_transition_with_extraBtn
- 화면 이동 시간 측정 함수_2
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. {init_button} 클릭 <- 해당 부분이 추가됨
2. start_element 대기
3. action 클릭
4. {action2~3} 클릭 <- 해당 부분이 추가됨
5. end_element 가 확인되면 종료
6. [옵션] end_button이 정의되어 있을 경우 end_button 누르고 종료
"""
def measure_screen_transition_with_extraBtn(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """특정 화면(A)에서 화면(B)으로 이동하는 데 걸리는 시간을 측정"""

    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    driver.implicitly_wait(0)  # Explicit wait만 사용하여 대기 시간 최적화

    transition_times = []

    try:
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2)
            driver.activate_app(app_package)

            init_btn_by, init_btn_element = get_locator_strategy(test_info["init_button"], platform_name)
            start_by, start_element = get_locator_strategy(test_info["start_element"], platform_name)
            action_by, action_element = get_locator_strategy(test_info["action"], platform_name)
            end_by, end_element = get_locator_strategy(test_info["end_element"], platform_name)

            try:
                init_btn = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((init_btn_by, init_btn_element))
                )
                init_btn.click()
                log_signal.emit("✅ 초기 버튼 클릭 완료")
            except TimeoutException:
                log_signal.emit("❌ 초기 버튼 탐색 실패")
                continue

            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((start_by, start_element))
                )
            except TimeoutException:
                log_signal.emit("❌ 시작 화면 탐색 실패")
                continue

            try:
                action = driver.find_element(action_by, action_element)
                action.click()
            except:
                log_signal.emit("❌ 액션 버튼을 찾을 수 없음")
                continue

            # 🔹 action2 존재하는 경우 클릭 수행
            if "action2" in test_info:
                try:
                    action2_by, action2_element = get_locator_strategy(test_info["action2"], platform_name)
                    log_signal.emit(f"🔍 init_button2 확인: ({action2_by}, {action2_element})")
                    
                    action2 = WebDriverWait(driver, wait_time).until(
                        EC.element_to_be_clickable((action2_by, action2_element))
                    )
                    action2.click()
                    log_signal.emit("✅ action2 클릭 완료")
                except TimeoutException:
                    log_signal.emit("❌ action2 요소 탐색 실패")
                    continue

            # 🔹 action3 존재하는 경우 클릭 수행
            if "action3" in test_info:
                try:
                    action3_by, action3_element = get_locator_strategy(test_info["action3"], platform_name)
                    log_signal.emit(f"🔍 action3 확인: ({action3_by}, {action3_element})")
                    
                    action3 = WebDriverWait(driver, wait_time).until(
                        EC.element_to_be_clickable((action3_by, action3_element))
                    )
                    action3.click()
                    log_signal.emit("✅ action3 클릭 완료")
                except TimeoutException:
                    log_signal.emit("❌ action3 요소 탐색 실패")
                    continue

            log_signal.emit("✅ 버튼 클릭 완료, 화면 전환 시작")
            start_time = time.time()

            try:
                WebDriverWait(driver, wait_time, poll_frequency=0.1).until(
                    EC.presence_of_element_located((end_by, end_element))
                )
                end_time = time.time()
                transition_time = end_time - start_time
                transition_times.append(transition_time)
                log_signal.emit(f"✅ 화면 전환 완료: {transition_time:.2f} 초")
            except TimeoutException:
                log_signal.emit("❌ 화면 전환 실패")

            try:
                end_button_by, end_button_element = get_locator_strategy(test_info["end_button"], platform_name)
                action_elem = driver.find_element(end_button_by, end_button_element)
                action_elem.click()
            except Exception as e:
                log_signal.emit("⚠️ 마지막 요소 클릭 실패(혹은 미설정)")

            time.sleep(1)

    finally:
        driver.quit()

    avg_time = sum(transition_times) / len(transition_times) if transition_times else 0
    return transition_times, avg_time


""" measure_search_time
- Text 입력이 필요한 화면 이동 시간 측정 함수
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. init_element 대기
2. init_button 클릭
3. [옵션] init_button2 클릭
4. input_field 대기
5. search_text 전송
6. search_button 클릭
7. end_element 가 확인되면 종료
8. [옵션] end_button이 정의되어 있을 경우 end_button 누르고 종료
"""
def measure_search_time(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """검색어 입력 후 검색 결과가 나타날 때까지의 시간을 측정"""

    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    driver.implicitly_wait(0)  # Explicit wait만 사용하여 대기 시간 최적화

    search_times = []

    try:
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2)
            driver.activate_app(app_package)

            init_by, init_element = get_locator_strategy(test_info["init_element"], platform_name)
            init_btn_by, init_btn_element = get_locator_strategy(test_info["init_button"], platform_name)
            input_by, input_element = get_locator_strategy(test_info["input_field"], platform_name)
            search_by, search_element = get_locator_strategy(test_info["search_button"], platform_name)
            end_by, end_element = get_locator_strategy(test_info["end_element"], platform_name)

            try:
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((init_by, init_element))
                )
            except TimeoutException:
                log_signal.emit("❌ 초기 화면 탐색 실패")
                continue    

            try:
                init_button = driver.find_element(init_btn_by, init_btn_element)
                init_button.click()

                # 🔹 init_button2 존재하는 경우 클릭 수행
                if "init_button2" in test_info:
                    try:
                        init_btn2_by, init_btn2_element = get_locator_strategy(test_info["init_button2"], platform_name)
                        log_signal.emit(f"🔍 init_button2 확인: ({init_btn2_by}, {init_btn2_element})")
                        
                        init_button2 = WebDriverWait(driver, wait_time).until(
                            EC.element_to_be_clickable((init_btn2_by, init_btn2_element))
                        )
                        init_button2.click()
                        time.sleep(1)  # 클릭 후 잠시 대기
                        log_signal.emit("✅ start_element_2 클릭 완료")
                    except TimeoutException:
                        log_signal.emit("❌ start_element_2 요소 탐색 실패 (무시하고 진행)")
                        
                try:
                    search_input = WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((input_by, input_element))
                    )
                    search_input.clear()
                    search_input.send_keys(test_info["search_text"])
                    search_button = driver.find_element(search_by, search_element)
                    search_button.click()
                except Exception as e:
                    log_signal.emit(f"❌ input 요소 탐색 실패, {e}")
                
            except Exception as e:
                log_signal.emit(f"에러 발생: {e}")
                continue

            start_time = time.time()
            
            try:
                WebDriverWait(driver, wait_time, poll_frequency=0.1).until(
                    EC.presence_of_element_located((end_by, end_element))
                )
                end_time = time.time()
                search_time = end_time - start_time
                search_times.append(search_time)
                log_signal.emit(f"✅ 검색 완료 시간: {search_time:.2f} 초")
            except TimeoutException:
                log_signal.emit("❌ 결과 요소 탐색 실패")

            try:
                end_button_by, end_button_element = get_locator_strategy(test_info["end_button"], platform_name)
                action_elem = driver.find_element(end_button_by, end_button_element)
                action_elem.click()
            except Exception as e:
                log_signal.emit("⚠️ 마지막 요소 클릭 실패(혹은 미설정)")

            time.sleep(1)

    finally:
        driver.quit()

    avg_time = sum(search_times) / len(search_times) if search_times else 0
    return search_times, avg_time
