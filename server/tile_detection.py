import cv2
import detection
import boto3
from tile_score import TileId, score
import sys
import os
from datetime import datetime
import random
import shutil

CONFIG = "./yolov3-tile.cfg"
CLASSES = [
    "back",
    "m1",
    "m2",
    "m3",
    "m4",
    "m5",
    "m6",
    "m7",
    "m8",
    "m9",
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8",
    "p9",
    "s1",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
    "s8",
    "s9",
    "chun",
    "hatsu",
    "haku",
    "nan",  # winds-nan
    "pei",  # winds-pei
    "sha",  # winds-sha
    "ton",  # winds-ton
]

# convert class_id to tile id used in tile_score.
CLASSID_TO_SCORE_TILE_ID = [
    # BACK
    int(TileId.BACK),
    # MAN
    int(TileId.MAN1),
    int(TileId.MAN2),
    int(TileId.MAN3),
    int(TileId.MAN4),
    int(TileId.MAN5),
    int(TileId.MAN6),
    int(TileId.MAN7),
    int(TileId.MAN8),
    int(TileId.MAN9),
    # PIN
    int(TileId.PIN1),
    int(TileId.PIN2),
    int(TileId.PIN3),
    int(TileId.PIN4),
    int(TileId.PIN5),
    int(TileId.PIN6),
    int(TileId.PIN7),
    int(TileId.PIN8),
    int(TileId.PIN9),
    # SOU
    int(TileId.SOU1),
    int(TileId.SOU2),
    int(TileId.SOU3),
    int(TileId.SOU4),
    int(TileId.SOU5),
    int(TileId.SOU6),
    int(TileId.SOU7),
    int(TileId.SOU8),
    int(TileId.SOU9),
    # CHUN,HATSU,HAKU
    int(TileId.CHUN),
    int(TileId.HATSU),
    int(TileId.HAKU),
    # TON,NAN,SHA,PEI
    int(TileId.NAN),
    int(TileId.PEI),
    int(TileId.SHA),
    int(TileId.TON),
]

WEIGHTS_BUCKET = "tile-score-weights"
WEIGHTS_NAME = "yolov3-tile_900.weights"
IMAGES_BUCKET = "tile-score-images"
IMAGE_NAME = "object-detection.jpg"
DIR_NAME = "/tmp"

WEIGHTS_NAME_DEFAULT = f"{DIR_NAME}/{WEIGHTS_NAME}"


def download_weights(weights_name=WEIGHTS_NAME_DEFAULT):
    if os.path.exists(weights_name):
        return
    if os.path.exists(f"./{WEIGHTS_NAME}"):
        shutil.copyfile(f"./{WEIGHTS_NAME}", weights_name)
    else:
        s3 = boto3.client("s3")
        s3.download_file(WEIGHTS_BUCKET, WEIGHTS_NAME, weights_name)


def upload_image(image, category):
    now = datetime.now()
    image_name = f"{now:%Y%m%d%H%M}-{random.randint(0, 100000):05}.png"
    cv2.imwrite(f"{DIR_NAME}/{image_name}", image)
    yearmonth = f"{now:%Y%m}"
    s3 = boto3.client("s3")
    s3.upload_file(
        f"{DIR_NAME}/{image_name}", IMAGES_BUCKET, f"{category}/{yearmonth}/{image_name}",
    )


def draw_bounding_boxes(image, predict_results):
    return detection.draw_bounding_boxes(image, CLASSES, predict_results)


def predict_bounding_boxes(image, weights_name=WEIGHTS_NAME_DEFAULT, config=CONFIG):
    return detection.predict_bounding_boxes(image, weights_name, config, CLASSES)


def convert_to_rectangle(predict_results, class_id_converter=None):
    score_boxes = []
    for result in predict_results:
        box = result["box"]
        class_id = result["class_id"]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        score_boxes.append(
            [
                class_id_converter[class_id] if class_id_converter is not None else class_id,
                round(x),
                round(y),
                round(x + w),
                round(y + h),
            ]
        )
    return score_boxes


def convert_to_score_boxes(predict_results):
    return convert_to_rectangle(predict_results, CLASSID_TO_SCORE_TILE_ID)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--weight", help="weight file", default=f"{DIR_NAME}/{WEIGHTS_NAME}")
    parser.add_argument("--input", help="input image file")
    parser.add_argument("--output", help="output image file", default=f"{DIR_NAME}/{IMAGE_NAME}")
    parser.add_argument("--config", help="config file", default=CONFIG)
    args = parser.parse_args()

    print(f"opencv version: {cv2.__version__}")
    weights_name = args.weight
    image_name = args.output
    # download_weight(weights_name)
    image = cv2.imread(args.input)
    results = predict_bounding_boxes(image, weights_name, args.config)
    score_boxes = convert_to_score_boxes(results)
    print(score_boxes)
    score(score_boxes, True, 256)
    image = draw_bounding_boxes(image, results)
    cv2.imwrite(image_name, image)
    # upload_image(image_name)
