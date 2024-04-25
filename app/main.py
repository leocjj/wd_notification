from typing import Union, Dict, Any
from fastapi import FastAPI
import pika
import app.db_orm as orm

orm.create_preferences_table()
app = FastAPI()


@app.get("/")
def read_root():
    """ Base endpoint to check the API status """
    result = orm.get_preferences_number_of_rows()
    if result is None:
        return {"Notification API status": "Inactive"}
    # TODO: check if the number of rows is needed
    return {"Notification API status": f"{result} Active"}


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
    channel.exchange_declare(exchange='sms', exchange_type='topic')
    
    routing_key = "sms"
    message = 'Hello World 2!'
    channel.basic_publish(exchange='sms', routing_key=routing_key, body=message)
    print(f" [x] Sent {routing_key}:{message}")
    connection.close()
    return {"message": f" [x] Sent {routing_key}:{message}"}


@app.post('/')
def main(payload: Dict[Any, Any]):
    return payload
