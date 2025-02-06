import subprocess
import platform

def get_android_device():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        for line in result.stdout.split("\n")[1:]:
            if line.strip() and "device" in line:
                return line.split("\t")[0]
    except Exception as e:
        print(f"Android 디바이스 검색 오류: {e}")
    return None

def get_ios_device():
    """연결된 iOS 기기 ID 가져오기 (Windows에서는 예외 처리)"""
    if platform.system() == "Windows":
        print("⚠️ Windows에서는 iOS 기기 탐색이 지원되지 않습니다.")
        return None  # Windows에서는 iOS 기기를 찾을 수 없음

    try:
        output = subprocess.check_output(["idevice_id", "-l"], universal_newlines=True)
        devices = output.strip().split("\n")
        return devices[0] if devices else None
    except FileNotFoundError:
        print("❌ 'idevice_id' 명령어를 찾을 수 없습니다. macOS에서 libimobiledevice를 설치하세요.")
        return None
    except Exception as e:
        print(f"❌ iOS 디바이스 검색 오류: {e}")
        return None

