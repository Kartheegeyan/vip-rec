import cv2
import zmq
import time
from loguru import logger


class OpenCVCamera:
    def __init__(self, device_id, fps):
        self.device_id = device_id
        self.fps = fps

        self.cap = cv2.VideoCapture(self.device_id)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not self.cap.isOpened():
            raise RuntimeError(f"[ImageServer] Failed to open camera {device_id}")

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self):
        self.cap.release()


class ImageServer:
    def __init__(self, **kwargs):
        self.fps = kwargs.get("fps", 30)
        self.port = kwargs.get("port", 5555)
        self.device_id = kwargs.get("device_id", '/dev/video2')

        # ZMQ PUB
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.port}")

        # Init camera
        self.camera = OpenCVCamera(self.device_id, self.fps)

        logger.info("[ImageServer] Started")
        logger.info(f"[ImageServer] Camera {self.camera.device_id} ready")

    def close(self):
        self.camera.release()
        self.socket.close()
        self.context.term()
        logger.info("[ImageServer] Closed")

    def send_process(self):
        try:
            while True:
                frame = self.camera.get_frame()
                print(f"[ImageServer] Sending frame {frame}")

                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    print("[ImageServer] JPEG encode failed")
                    continue

                self.socket.send(buffer.tobytes())

                # Optional FPS control (soft)
                time.sleep(1.0 / self.fps)

        except KeyboardInterrupt:
            print("[ImageServer] Interrupted by user")
        finally:
            self.close()


if __name__ == "__main__":
    server = ImageServer()
    server.send_process()
