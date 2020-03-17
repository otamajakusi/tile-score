import cv2
import detection
import boto3

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

def draw_bounding_boxes():
    image = cv2.imread(IMAGE)
    s3 = boto3.client('s3')
    s3.download_file(WEIGHTS_BUCKET, WEIGHTS_NAME, f"/tmp/{WEIGHTS_NAME}")

    image = detection.draw_bounding_boxes(image, f"/tmp/{WEIGHTS_NAME}", CONFIG, CLASSES)
    cv2.imwrite("/tmp/object-detection.jpg", image)
    s3.upload_file("/tmp/object-detection.jpg", IMAGES_BUCKET)

