import cv2
import detection
import boto3
import os

IMAGE = "./202002030632-52248.png"
CONFIG = "./yolov3-tile.cfg"
CLASSES = [
        "bk",
        "m1","m2","m3","m4","m5","m6","m7","m8","m9",
        "p1","p2","p3","p4","p5","p6","p7","p8","p9",
        "s1","s2","s3","s4","s5","s6","s7","s8","s9",
        "sc","sh","sw",
        "wn","wp","ws","wt",]

WEIGHTS_BUCKET = "tile-score-weights"
WEIGHTS_NAME = "yolov3-tile_900.weights"
IMAGES_BUCKET = "tile-score-images"
IMAGE_NAME = "object-detection.jpg"
DIR_NAME = "/tmp"

def draw_bounding_boxes():
    print(f"opencv version: {cv2.__version__}")
    image = cv2.imread(IMAGE)
    s3 = boto3.client('s3')
    if not os.path.isfile(f"{DIR_NAME}/{WEIGHTS_NAME}"):
        s3.download_file(WEIGHTS_BUCKET, WEIGHTS_NAME, f"{DIR_NAME}/{WEIGHTS_NAME}")

    image = detection.draw_bounding_boxes(image, f"{DIR_NAME}/{WEIGHTS_NAME}", CONFIG, CLASSES)
    cv2.imwrite(f"{DIR_NAME}/{IMAGE_NAME}", image)
    s3.upload_file(f"{DIR_NAME}/{IMAGE_NAME}", IMAGES_BUCKET, IMAGE_NAME)

if __name__ == '__main__':
    draw_bounding_boxes()
