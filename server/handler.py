import json
import tile_detection
import param
import os
import tile_score
from yaku_ja import YAKU_JA as YAKU_NAME


def ping(event, context):
    return {"statusCode": 200, "body": "pong"}


def _score(event, context):
    params = {}
    body = json.loads(event["body"])
    valid = param.is_valid_param(body, params)
    image = params.get("image")
    tsumo = params.get("tsumo")
    if not valid:
        return {"statusCode": 400, "body": json.dumps({"error": "data"})}, image

    tile_detection.download_weights()
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
    scores["boxes"] = tile_detection.convert_to_rectangle(predict, tile_detection.CLASSES)
    scores["width"] = width
    scores["height"] = height
    print(scores)
    return {"statusCode": 200, "body": json.dumps(scores)}, image


def score(event, context):
    image = None
    try:
        resp, image = _score(event, context)
        status_code = resp["statusCode"]
        return resp
    except Exception as e:
        print(e)
        resp = {"statusCode": 500, "body": "internal server error"}
        status_code = resp["statusCode"]
        return resp
    finally:
        print(status_code)
        image_category = "image"
        if os.environ.get("STAGE") == "dev":
            image_category += "-dev"
        if status_code is None:
            image_category += "-500"
        elif status_code != 200:
            image_category += f"-${str(status_code)}"
        if image is not None:
            tile_detection.upload_image(image, image_category)
