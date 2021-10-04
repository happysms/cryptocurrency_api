from cryptocurrency_api.DBUpdater import DBUpdater
import os

host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')

def lambda_handler(event, context):
    db = DBUpdater(host, user, password)
    db.execute_daily()
