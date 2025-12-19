import pyzed.sl as sl
import cv2

zed = sl.Camera()

init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD720
init_params.camera_fps = 30
init_params.depth_mode = sl.DEPTH_MODE.NONE

if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
    raise RuntimeError("Failed to open ZED camera")

left = sl.Mat()

while True:
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(left, sl.VIEW.LEFT)
        frame = left.get_data()
        cv2.imshow("ZED Left", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

zed.close()
cv2.destroyAllWindows()
