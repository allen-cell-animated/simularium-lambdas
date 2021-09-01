import json


def lambda_handler(event, context):
    print("Testing")
    print(json.dumps(event))
    return json.dumps(event)
