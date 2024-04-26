from typing import Union, Dict, Any
from fastapi import FastAPI
import pika
import requests
import app.db_orm as orm


SMS = "sms"
EMAIL = "email"

app = FastAPI()


@app.get("/")
def read_root():
    """ Base endpoint to check the API status """
    result = orm.get_preferences_number_of_rows()
    if result is None:
        return {"Notification API status": "Inactive"}
    return {"Notification API status": f"({result}) Active"}


@app.get("/v1/preferences/{user_id}")
def read_item(user_id: int, q: Union[str, None] = None):
    """ Get preferences by user id """
    result = orm.get_preferences_by_user_id(user_id)
    if result is None:
        return {"Error":"user id does not exist, create it with a POST."}
    return {"user_id": user_id, "email_enabled": result.email_enabled, "sms_enabled": result.sms_enabled}


@app.post("/v1/preferences/{user_id}")
def create_preference(user_id: int, email_enabled: bool, sms_enabled: bool):
    """ Create a new preference"""
    result = orm.upsert_preferences(user_id, bool(email_enabled), bool(sms_enabled))
    return {"user_id": user_id, "email_enabled": result.email_enabled, "sms_enabled": result.sms_enabled}


@app.post("/v1/notifications")
def create_notification():
    """ Create a new notification """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='news', exchange_type='topic')

    # get the users email and phone from the mocked database
    users = orm.inner_join_users_preferences()

    # get the new properties from the mocked endpoint /v1/properties/news
    response = requests.get('http://127.0.0.1:8000/v1/properties/news')
    properties = response.json()['news']

    # send the notifications according to the user preferences
    for user in users:
        if user[0].email_enabled:
            temp = properties + [f"{user[1].email}"]
            channel.basic_publish(exchange='news', routing_key=EMAIL, body=str(temp))
        if user[0].sms_enabled:
            temp = properties + [f"{user[1].phone}"]
            channel.basic_publish(exchange='news', routing_key=SMS, body=str(temp))

    connection.close()
    return {"result": "Notifications created!"}

# Mock the external property databases access through APIs
@app.get('/v1/properties/news')
def news():
    properties = orm.get_properties()
    message = []
    for prop in properties:
        message.append(f"\nProperty code: {prop.id}\n{prop.name}\n{str(prop.price)}\n\n")

    return {"news": message}
