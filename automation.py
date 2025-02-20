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
from appium.webdriver.applicationstate import ApplicationState

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

    if not element_info:
        raise ValueError("❌ 요소 정보가 유효하지 않습니다.")

    locator_strategy = element_info.get("locator_strategy", {}).get(platform_key, "XPATH")
    locator_value = element_info.get("value", {}).get(platform_key, None)

    if not locator_value:
        raise ValueError(f"❌ '{platform_key}'에 대한 locator 값이 없습니다!")

    return LOCATOR_MAPPING.get(locator_strategy, By.XPATH), locator_value


def execute_step(driver, step_info, platform_name, log_signal, start_time_ref, launch_times, wait_time):
    """단계별 액션을 실행하고, 필요하면 시간 측정을 시작/종료"""
    action_type = step_info.get("action")
    measure_type = step_info.get("measure")  # 측정 시작/종료 속성
    desciption = step_info.get("description", "Description 작성 안됨")

    try:
        by_strategy, element_value = get_locator_strategy(step_info, platform_name)

        if measure_type == "launch":
            start_time_ref["time"] = time.time()
            log_signal.emit("⏱️ 측정 시작")

        if action_type == "touch":
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((by_strategy, element_value))
            )
            element.click()
            log_signal.emit(f"👉 터치 성공: {element_value} // {desciption}")

        elif action_type == "search":
            WebDriverWait(driver, 10, poll_frequency=0.1).until(
                EC.presence_of_element_located((by_strategy, element_value))
            )
            log_signal.emit(f"🔍 요소 탐색 성공: {element_value} // {desciption}")

        elif action_type == "send":
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by_strategy, element_value))
                )
            element.clear()
            element.send_keys(step_info.get("text", ""))
            log_signal.emit(f"⌨️ 텍스트 입력 성공: {step_info.get('text', '')} // {desciption}")

        elif action_type == "contains":
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((by_strategy, element_value))
            )

            # ✅ 기본 값 설정 (TextView가 없을 경우 대비)
            text_value = None
            found_texts = []

            # ✅ TextView 요소가 직접 탐색된 경우
            if element.tag_name == "android.widget.TextView":
                text_value = element.get_attribute("text").strip()
                found_texts.append(text_value)

            # ✅ android.view.View 내부에서 모든 TextView 찾기
            textviews = element.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")

            # ✅ TextView에서 text 속성 가져오기
            text_values = [tv.get_attribute("text").strip() for tv in textviews if tv.get_attribute("text").strip()]
            found_texts.extend(text_values)

            if not found_texts:
                log_signal.emit(f"❌ TextView 요소가 존재하지 않음. // {desciption}")
            else:
                # ✅ 찾은 모든 텍스트를 출력 및 검증
                match_found = False
                for text in found_texts:
                    if step_info.get("text") in text:
                        log_signal.emit(f"✅ 찾은 Text: {text} // {desciption}")
                        match_found = True

                if not match_found:
                    log_signal.emit(f"❌ TextView 요소는 있으나, '{step_info.get('text')}' 포함된 값 없음.")

            
        if measure_type == "start":
            start_time_ref["time"] = time.time()
            log_signal.emit("⏱️ 측정 시작")

        elif measure_type in ["end", "launch"]:
            if start_time_ref["time"]:
                elapsed_time = time.time() - start_time_ref["time"]
                launch_times.append(elapsed_time)
                log_signal.emit(f"✅ 측정 완료: {elapsed_time:.2f} 초")
                start_time_ref["time"] = None  # 측정 종료 후 초기화

    except TimeoutException:
        log_signal.emit(f"❌ 요소 탐색 실패: {element_value} // {desciption}")
    except Exception as e:
        log_signal.emit(f"⚠️ 에러 발생: {str(e)}")


def execute_test_steps(app_package, app_activity, test_info, device_name, platform_name, wait_time=10, test_count=10, log_signal=None):
    """테스트 단계 실행 및 측정 시간 반환"""

    driver = setup_driver(platform_name, app_package, app_activity, device_name)
    driver.implicitly_wait(0)  # Explicit wait만 사용하여 대기 시간 최적화

    start_time_ref = {"time": None}  # 측정 시작 시간 참조 변수
    launch_times = []  # 측정된 시간 저장 리스트

    test_names = ", ".join(test_info.keys())

    try: 
        for i in range(test_count):
            log_signal.emit(f"테스트 {i + 1}/{test_count} 시작")

            driver.terminate_app(app_package)
            time.sleep(2) #정상 종료 대기
            log_signal.emit("🚀 앱 실행 및 측정 시작")
            driver.activate_app(app_package)

            for step_name, step_info in test_info.items():
                if step_name.startswith("step"):
                    execute_step(driver, step_info, platform_name, log_signal, start_time_ref, launch_times, wait_time)

    except Exception as e:
        log_signal.emit(f"❌ 측정 중 알 수 없는 에러 발생: {e}")

    finally:
        # ✅ 마지막 액션 후 앱 종료
        driver.terminate_app(driver.current_package)

    avg_time = sum(launch_times) / len(launch_times) if launch_times else 0
    return launch_times, avg_time