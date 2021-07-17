""" DB Requests
"""

import json
from requests import post, get

BASE_URL = "http://ec2-18-130-251-69.eu-west-2.compute.amazonaws.com"

data = {
    "first_name": "vs_DB_API1",
    "last_name": "Smith",
    "building": "11",
    "street": "Indigo Avenue",
    "town": "Newcastle",
    "county": "Tyne and Wear",
    "postcode": "NE2 3JM",
    "telephone_number": "07777777778",
    "email_address": "me@me.com",
    "preferred_time_to_contact": "S",
    "annual_income": "30000",
    "loan_amount": "50000",
    "property_value": "1000000",
    "mortgage_type": "RM",
    "ltv_value": "50"
}

# Simulate sending from SNS
data2 = {
    "Message": "{\"first_name\": \"vs_DB_API_simulate_SNS\",\"last_name\": \"Stevenson\",\"ltv_value\": \"34.89\",\"telephone_number\": \"07777456278\"}"
}

sns_header = {"X-Amz-Sns-Message-Type": "Notification"}


response = get(BASE_URL + "/")
print("GET Healthcheck... (/)")
print("Response: " + response.text)

response = get(BASE_URL + "/log")
print("GET Log ... (/log)")
print("Response: " + response.text)

response = get(BASE_URL + "/get-all-enquiries")
print("GET all Enquiries... (/get-all-enquiries)")
print("Response: " + response.text)

response = post(BASE_URL + "/add-enquiry", json = data)
print("POST Add Enquiry... (/add-enquiry)")
print("Response: " + response.text)

response = post(BASE_URL + "/add-enquiry-sns", headers=sns_header, json = data2)
print("POST Add Enquiry, simulated from SNS... (/add-enquiry-sns)")
print("Response: " + response.text)