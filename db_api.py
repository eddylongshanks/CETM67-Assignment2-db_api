""" db API
"""

from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse, abort
import json
import requests
import boto3
import botocore.exceptions
import uuid

dynamodb = boto3.resource('dynamodb')

app = Flask(__name__)
api = Api(app)

## Resources ##
class GetAllEnquiries(Resource):
    def get(self):
        # Get table
        try:
            table = dynamodb.Table('Enquiry')
            enquiries = table.scan()
            return enquiries['Items']

        except Exception as e:
            log(e)
            response_message = str(type(e).__name__) + ": " + str(e)
            return response_object(500, response_message)


class AddEnquiry(Resource):
    def post(self):
        try:
            data = json.loads(request.data)
            # Generate an ID
            data['id'] = get_guid()
            log(data)

            table = dynamodb.Table('Enquiry')
            table.put_item(
                Item = data
            )

            response_message = json.dumps(data)
            return response_object(201, response_message)

        except Exception as e:
            log(e)
            response_message = str(type(e).__name__) + ": " + str(e)
            return response_object(500, response_message)


class AddEnquirySNS(Resource):
    def post(self):
        try:
            data = json.loads(request.data)

            header = request.headers.get('X-Amz-Sns-Message-Type')
            # Perform check for subscription confirmation request, subscribe to the SNS topic
            if header == 'SubscriptionConfirmation' and 'SubscribeURL' in data:
                r = requests.get(data['SubscribeURL'])

            if header == 'Notification':
                enquiry = process_sns(data)
                log("Ready Enquiry: " + str(enquiry))

                table = dynamodb.Table('Enquiry')
                table.put_item(
                    Item = enquiry
                )

                response_message = json.dumps(enquiry)
                return response_object(201, response_message)
            else:
                response_message = json.dumps(data)
                return response_object(400, response_message)

        except Exception as e:
            log(e)
            response_message = json.dumps(str(e))
            return response_object(500, response_message)


class GetLog(Resource):
    def get(self):
        f = open('db_log.txt', 'r')
        return f.read()


class HealthCheck(Resource):
    def get(self):
        response_message = 'DB API Available'
        return response_object(200, response_message)


## Routing ##
api.add_resource(HealthCheck, '/')
api.add_resource(GetLog, '/log')
api.add_resource(GetAllEnquiries, '/get-all-enquiries')
api.add_resource(AddEnquiry, '/add-enquiry')
api.add_resource(AddEnquirySNS, '/add-enquiry-sns')

# Methods

def process_sns(msg):
    # Converts the contents of the message string to a dictionary object
    js = json.loads(msg['Message'])

    # Adds a randomly generated Id to the object
    js['id'] = get_guid()

    return js

def get_guid():
    # Generate a Guid for the ID
    return str(uuid.uuid4())

def log(data_to_save):
    # Logs data to a local file for debugging
    with open('db_log.txt', 'w') as log_file:
        log_file.write(str(data_to_save))
        log_file.write("\n")

def response_object(status_code, message):
    # encapsulates the return object
    return {
        'statusCode': status_code,
        'body': message
    }

if __name__ == "__main__":
    app.run(debug=True)