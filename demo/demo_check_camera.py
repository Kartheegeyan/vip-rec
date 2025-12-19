import cv2
import glob

def check_cameras():
    devices = sorted(glob.glob("/dev/video*"))

    if not devices:
        print("No /dev/video devices found")
        return

    for dev in devices:
        idx = int(dev.replace("/dev/video", ""))
        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)

        if not cap.isOpened():
            print(f"{dev}: ❌ cannot open")
            continue

        ret, frame = cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            print(f"{dev}: ✅ OK ({w}x{h})")
        else:
            print(f"{dev}: ❌ opened but no frames")

        cap.release()


if __name__ == "__main__":
    check_cameras()
