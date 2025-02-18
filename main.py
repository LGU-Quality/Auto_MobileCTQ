import sys
from PyQt5.QtWidgets import QApplication
from ui_main import AutomationApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomationApp()
    window.show()
    sys.exit(app.exec_())

temp = {
  "platformName": "Android",
  "appium:automationName": "uiautomator2",
  "appium:deviceName": "192.168.219.105:41089",
  "appium:appPackage": "uplus.membership",
  "appium:appActivity": "com.uplus.membership.smart.ui.main.MainActivity",
  "appium:noReset": true,
  "appium:fullReset": false
}

temp = {
  "platformName": "Android",
  "appium:automationName": "uiautomator2",
  "appium:deviceName": "R3CXA0BY0SK",
  "appium:appPackage": "com.lguplus.aicallagent",
  "appium:appActivity": "com.lguplus.aicallagent.MainActivity",
  "appium:noReset": true,
  "appium:fullReset": false
}

""" measure_app_launch_time
- 앱 실행 시간 속도 측정 함수
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. success_element 가 탐색되는 즉시 종료
"""
""" measure_screen_transition
- 화면 이동 시간 측정 함수
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. {start_element} 대기
2. action 클릭
3. end_element 가 확인되면 종료
4. [옵션] end_button이 정의되어 있을 경우 end_button 누르고 종료
"""
""" measure_screen_transition_with_extraBtn
- 화면 이동 시간 측정 함수_2
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. {init_button} 클릭 <- 해당 부분이 추가됨
2. start_element 대기
3. action 클릭
4. [옵션] (action2~3) 클릭 <- 해당 부분이 추가됨
5. end_element 가 확인되면 종료
6. [옵션] end_button이 정의되어 있을 경우 end_button 누르고 종료
"""
""" measure_search_time
- Text 입력이 필요한 화면 이동 시간 측정 함수
- 필요 Config 및 동작 순서: 
0. 앱 실행
1. init_element 대기
2. init_button 클릭!
3. [옵션] init_button2 클릭!
4. input_field 대기
5. {search_text} 전송
6. search_button 클릭
7. end_element 가 확인되면 종료
8. [옵션] end_button이 정의되어 있을 경우 end_button 누르고 종료
"""

# https://github.com/LGU-Quality/Auto_MobileCTQ.git