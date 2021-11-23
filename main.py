from DBUpdater import DBUpdater

if __name__ == "__main__":
    df = DBUpdater(host="localhost",
                   user="root",
                   password="khuminsung12!")

    db.execute_daily()
