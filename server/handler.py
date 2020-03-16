import json
import tile_detection


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    try:
        tile_detection.draw_bounding_boxes()
    except Exception as e:
        response["body"] = e

    return response
