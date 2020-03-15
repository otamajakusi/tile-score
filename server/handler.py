import cv2 as cv
import json


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "opencv": f"{cv.__version__}"
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
