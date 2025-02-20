import time
from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ✅ Locator 전략 매핑
LOCATOR_MAPPING = {
    "ID": AppiumBy.ID,
    "XPATH": AppiumBy.XPATH,
    "ANDROID_UIAUTOMATOR": AppiumBy.ANDROID_UIAUTOMATOR,
    "IOS_PREDICATE": AppiumBy.IOS_PREDICATE,
    "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID,
    "CLASS_NAME": AppiumBy.CLASS_NAME
}


def setup_driver():
    options = AppiumOptions()
    options.load_capabilities({
        "platformName": "Android",
        "appium:automationName": "uiautomator2",
        "appium:appPackage": "com.lguplus.aicallagent",
        "appium:appActivity": "com.lguplus.aicallagent.MainActivity",
        "appium:noReset": True,
        "appium:fullReset": False,
    })

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    return driver

def find_textview_inside_view(driver, timeout=10):
    """
    `new UiSelector().className("android.view.View").instance(10)` 내에 있는 `TextView` 요소 찾기

    :param driver: Appium WebDriver 객체
    :param timeout: 최대 대기 시간 (기본값: 10초)
    :return: (True, text_values) - text 값이 존재하는 경우
             (False, None) - text 값이 없는 경우
    """

    driver.terminate_app("com.lguplus.aicallagent")
    time.sleep(2)
    driver.activate_app("com.lguplus.aicallagent")
    

    try:
        # ✅ 특정 View 찾기 (ANDROID_UIAUTOMATOR 사용)
        view_selector = 'new UiSelector().className("android.view.View").instance(10)'

        view_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, view_selector))
        )

        if not view_element:
            print("❌ 특정 android.view.View 요소를 찾을 수 없음.")
            return False, None

        # ✅ view_element 자체가 TextView인 경우 → 바로 text 속성 확인
        if view_element.tag_name == "android.widget.TextView":
            text_value = view_element.get_attribute("text").strip()
            if text_value:
                print(f"✅ 찾은 TextView 값: {text_value}")
                return True, [text_value]
            else:
                print("❌ TextView 요소가 있지만, text 값이 없음.")
                return False, None

        # ✅ `View` 내부에서 `TextView`만 추출
        textviews = view_element.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")

        text_values = [tv.get_attribute("text") for tv in textviews if tv.get_attribute("text").strip()]

        if text_values:
            print(f"✅ 찾은 TextView들: {text_values}")
            return True, text_values

        print("❌ 특정 View 내에서 TextView의 text 값이 없음.")
        return False, None

    except TimeoutException:
        print("❌ 특정 View 내에서 TextView 요소를 찾을 수 없음.")
        return False, None
    


# ✅ 실행 예제
if __name__ == "__main__":
    platform = "Android"  # 또는 "iOS"
    driver = setup_driver()

    result, text_values = find_textview_inside_view(driver)

    print(f"🔹 최종 결과: {result}, 찾은 값: {text_values}")

    print("🔹 최종 결과:", result)
    driver.quit()
