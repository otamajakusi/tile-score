import json
import tile_detection
import param
import base64
import sys
import cv2
from tile_score import score


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    try:
        tile_detection.draw_bounding_boxes()
    except Exception as e:
        response["body"] = e

    return response


if __name__ == "__main__":
    result = {}
    with open(sys.argv[1], "rb") as f:
        image_encode = base64.b64encode(f.read())
    event = {"image": image_encode, "tsumo": True}
    param.is_valid_param(event, None, result)
    weights = f"{tile_detection.DIR_NAME}/{tile_detection.WEIGHTS_NAME}"
    image = result["image"]
    predict = tile_detection.predict_bounding_boxes(image, weights)
    score_boxes = tile_detection.convert_to_score_boxes(predict)
    height, width, _ = image.shape[:3]
    print(f"height:{height}, width:{width}")
    score(score_boxes, event["tsumo"], round(height / 2))
    image = tile_detection.draw_bounding_boxes(image, predict)
    cv2.imwrite(sys.argv[2] if len(sys.argv) > 2 else "predict.jpg", image)
