import cv2
import re
from deepface import DeepFace
from pathlib import Path
from loguru import logger
from config import DATA


class VIPFace:
    def __init__(self, **kwargs):
        self.db_path = kwargs.get('db_path', str(Path(DATA, "vip_images")))
        self.THRESHOLD = kwargs.get('THRESHOLD', 60)

    def draw_face(self, frame, r, name):
        x, y, w, h = int(r["source_x"]), int(r["source_y"]), int(r["source_w"]), int(r["source_h"])

        if name == 'UNKNOWN':
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            cv2.putText(
                frame, name,
                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 0, 255), 2
            )
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.putText(
                frame, name,
                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 255, 0), 2
            )

        return frame

    def run(self, **kwargs):
        port = kwargs.get('port', '/dev/video0')
        cap = cv2.VideoCapture(port)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            try:
                results = DeepFace.find(
                    img_path=frame,
                    db_path=self.db_path,
                    model_name="ArcFace",
                    detector_backend="retinaface",
                    enforce_detection=False
                )

                if len(results) > 0:  # detected
                    logger.debug(f"Detected no. of faces: {len(results)}")
                    df = results[0]
                    row = df.iloc[0]
                    logger.info(f"Row: {row}")

                    if row['confidence'] <= self.THRESHOLD:  # detected and face not in DB
                        name = 'UNKNOWN'
                    else:  # detected and face in DB
                        identity = Path(row['identity']).stem
                        name = identity
                        name = re.sub(r"\s*\d+$", "", name)

                    frame = self.draw_face(frame, row, name)

                    logger.info(f"Identity: {name}")
                    logger.info(f"Confidence: {row['confidence']}, Distance: {row['distance']}")

                else:  # no face detected
                    pass

            except Exception as e:
                logger.error(f"Error: {e}")

            cv2.imshow("Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


def main():
    vip_face = VIPFace()
    vip_face.run()


if __name__ == '__main__':
    main()
