import sys
from PyQt5.QtWidgets import QApplication
from ui_main import AutomationApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomationApp()
    window.show()
    sys.exit(app.exec_())
