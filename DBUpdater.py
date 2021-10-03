import pymysql


class DBUpdater:
    def __init__(self):
        self.conn = pymysql.connect(host='cryptocurrencydatabase.c5h79dp2k6f7.ap-northeast-2.rds.amazonaws.com',
                                    user='admin',
                                    password='khuminsung12!',
                                    db='cyripto',
                                    charset='utf8')

        with self.conn.cursor() as curs:
            crypto_list = ['KRW_BTC', 'KRW_ETH', "KRW_XRP", "KRW_ADA", "KRW_DOT", "KRW_DOGE"]

            for crypto in crypto_list:
                sql = f"""
                CREATE TABLE IF NOT EXISTS {crypto} (
                    id INT PRIMARY KEY,
                    Datetime TIMESTAMP,
                    open BIGINT(20),
                    high BIGINT(20),
                    low BIGINT(20),
                    close BIGINT(20),
                    volume BIGINT(20))
                """
                curs.execute(sql)

        self.conn.commit()

    def __del__(self):
        self.conn.close()
