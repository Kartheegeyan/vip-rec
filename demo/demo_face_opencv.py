import cv2
import re
from deepface import DeepFace
from pathlib import Path
from loguru import logger
from config import DATA


def save_source_image(frame, r):
    x, y, w, h = int(r["source_x"]), int(r["source_y"]), int(r["source_w"]), int(r["source_h"])

    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.putText(
        frame, "source",
        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.9, (0, 255, 0), 2
    )

    cv2.imwrite("source.png", frame)


def save_target_image(image, r):
    x, y, w, h = int(r["target_x"]), int(r["target_y"]), int(r["target_w"]), int(r["target_h"])

    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.putText(
        image, "target",
        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.9, (0, 255, 0), 2
    )

    cv2.imwrite("target.png", image)


db_path = Path(DATA, "vip_images")
THRESHOLD = 60

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        results = DeepFace.find(
            img_path=frame,
            db_path=str(db_path),
            model_name="ArcFace",
            detector_backend="retinaface",
            enforce_detection=False
        )

        if len(results) > 0:
            df = results[0]
            row = df.iloc[0]

            # save_source_image(frame, row)
            # target_img_path = row["identity"]
            # target_image = cv2.imread(target_img_path)
            # save_target_image(target_image, row)

            if row['confidence'] <= THRESHOLD:
                name = 'UNKNOWN'
            else:
                identity = Path(row['identity']).stem
                name = identity
                name = re.sub(r"\s*\d+$", "", name)

            logger.info(f"Identity: {name}")
            logger.info(f"Confidence: {row['confidence']}, Distance: {row['distance']}")

        else:
            print('no face detected')

    except Exception as e:
        print("Error:", e)

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
