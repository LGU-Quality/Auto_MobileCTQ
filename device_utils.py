import subprocess

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
    try:
        result = subprocess.run(["xcrun", "xctrace", "list", "devices"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "(Simulator)" not in line and "iPhone" in line:
                return line.split(" (")[1].split(")")[0]
    except Exception as e:
        print(f"iOS 디바이스 검색 오류: {e}")
    return None
