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

#  4.34
# 4.89
# 3초 내외가 나와야 함...