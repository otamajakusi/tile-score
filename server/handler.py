import json
import tile_detection
import param
import base64
import sys
import os
import cv2
import tile_score
from yaku_ja import YAKU_JA as YAKU_NAME


def ping(event, context):
    return {"statusCode": 200, "body": "pong"}


def _score(event, context):
    params = {}
    tile_detection.download_weights()
    if not param.is_valid_param(event, params):
        return {"statsuCode": 400, "body": json.dumps({"error": "data"})}

    image = params["image"]
    tsumo = params["tsumo"]
    predict = tile_detection.predict_bounding_boxes(image)
    score_boxes = tile_detection.convert_to_score_boxes(predict)
    height, width, _ = image.shape[:3]
    print(f"height:{height}, width:{width}")
    result = tile_score.score(score_boxes, tsumo, round(height / 2))
    scores = {}
    if result is None:
        scores["error"] = "invalid"
    elif result.error is not None and result.error != "There are no yaku in the hand":
        scores["error"] = result.error
    else:
        scores["han"] = result.han
        scores["fu"] = result.fu
        scores["yaku"] = (
            [] if result.yaku is None else [YAKU_NAME[yaku.name] for yaku in result.yaku]
        )
        scores["fu_details"] = [] if result.fu_details is None else result.fu_details
    scores["boxes"] = tile_detection.convert_to_score_boxes(predict)
    scores["width"] = width
    scores["height"] = height

    return {"statsuCode": 200, "body": json.dumps(scores)}


def score(event, context):
    try:
        resp = _score(event, context)
        status_code = resp["statusCode"]
        return resp
    except Exception as e:
        print(e)
        resp = {"statsuCode": 500, "body": "internal server error"}
        status_code = resp["statusCode"]
        return resp
    finally:
        image_category = "image"
        if status_code != 200:
            image_category += f"-{str(status_code)}"
        if os.environ.get("STAGE") == "dev":
            image_category += "-dev"
        tile_detection.upload_image(image, image_category)


if __name__ == "__main__":
    result = {}
    with open(sys.argv[1], "rb") as f:
        image_encode = base64.b64encode(f.read())
    tsumo = True
    event = {"image": image_encode, "tsumo": tsumo}
    param.is_valid_param(event, result)
    image = result["image"]
    predict = tile_detection.predict_bounding_boxes(image)
    score_boxes = tile_detection.convert_to_score_boxes(predict)
    height, width, _ = image.shape[:3]
    print(f"height:{height}, width:{width}")
    score_result = tile_score.score(score_boxes, tsumo, round(height / 2))
    image = tile_detection.draw_bounding_boxes(image, predict)
    cv2.imwrite(sys.argv[2] if len(sys.argv) > 2 else "predict.jpg", image)
