""" db API
"""
# pylint: disable=missing-function-docstring, no-self-use, invalid-name, broad-except, inconsistent-return-statements, unused-variable

import uuid
import json
import requests
import boto3
from flask import Flask, request
from flask_restful import Api, Resource, abort

dynamodb = boto3.resource('dynamodb')

app = Flask(__name__)
api = Api(app)

## Resources ##
class GetAllEnquiries(Resource):
    """ Return all Enquiries in the table """

    def get(self):
        try:
            table = dynamodb.Table('Enquiry')
            enquiries = table.scan()
            return enquiries['Items']

        except Exception as ex:
            log(ex)
            response_message = str(type(ex).__name__) + ": " + str(ex)
            abort(500, message=response_message)


class AddEnquiry(Resource):
    """ Add a new Enquiry """

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

        except Exception as ex:
            log(ex)
            response_message = str(type(ex).__name__) + ": " + str(ex)
            abort(500, message=response_message)


class AddEnquirySNS(Resource):
    """ Add a new Enquiry from SNS message """

    def post(self):
        try:
            data = json.loads(request.data)

            header = request.headers.get('X-Amz-Sns-Message-Type')
            # Perform check for subscription confirmation request, subscribe to the SNS topic
            if header == 'SubscriptionConfirmation' and 'SubscribeURL' in data:
                req = requests.get(data['SubscribeURL'])

            if header == 'Notification':
                enquiry = process_sns(data)
                log("Ready Enquiry: " + str(enquiry))

                table = dynamodb.Table('Enquiry')
                table.put_item(
                    Item = enquiry
                )

                response_message = json.dumps(enquiry)
                return response_object(201, response_message)

            response_message = json.dumps(data)
            abort(400, message=response_message)

        except Exception as ex:
            log(ex)
            response_message = json.dumps(str(ex))
            abort(500, message=response_message)


class GetLog(Resource):
    """ Return the log file (debug) """

    def get(self):
        with open('db_log.txt', 'r') as log_file:
            return log_file.read()


class HealthCheck(Resource):
    """ Check DB for access, return result """

    def get(self):
        try:
            table = dynamodb.Table('Enquiry')
            enquiries = table.scan()

            response_message = 'DB API Available. (CETM67 Assignment 2)'
            return response_object(200, response_message)

        except Exception as ex:
            log(ex)
            response_message = f'{type(ex).__name__}: DB API Unavailable. (CETM67 Assignment 2)'
            abort(500, message=response_message)


## Routing ##
api.add_resource(HealthCheck, '/')
api.add_resource(GetLog, '/log')
api.add_resource(GetAllEnquiries, '/get-all-enquiries')
api.add_resource(AddEnquiry, '/add-enquiry')
api.add_resource(AddEnquirySNS, '/add-enquiry-sns')

# Methods

def process_sns(msg):
    """ Converts the contents of the message string to a dictionary object """

    sns_message = json.loads(msg['Message'])

    # Adds a randomly generated Id to the object
    sns_message['id'] = get_guid()

    return sns_message

def get_guid():
    """ Generate a Guid for the ID """

    return str(uuid.uuid4())

def log(data_to_save):
    """ Logs data to a local file for debugging """

    with open('db_log.txt', 'w') as log_file:
        log_file.write(str(data_to_save))
        log_file.write("\n")

def response_object(status_code, message):
    """ encapsulates the return object """

    return {
        'statusCode': status_code,
        'body': message
    }

if __name__ == "__main__":
    app.run()
