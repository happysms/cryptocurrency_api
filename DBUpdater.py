import pymysql
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
import pyupbit
import time
import logging

class DBUpdater:

    def __init__(self):
        self.conn = pymysql.connect(host='cryptocurrencydatabase.c5h79dp2k6f7.ap-northeast-2.rds.amazonaws.com',
                                    user='admin',
                                    password='khuminsung12!',
                                    db='crypto',
                                    charset='utf8')

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.cryptos = ['KRW-BTC', 'KRW-ETH', "KRW-XRP", "KRW-ADA", "KRW-DOT", "KRW-DOGE"]
        self.crypto_tables = ['KRW_BTC', 'KRW_ETH', "KRW_XRP", "KRW_ADA", "KRW_DOT", "KRW_DOGE"]

        with self.conn.cursor() as curs:
            for crypto in self.crypto_tables:
                sql = f"""
                CREATE TABLE IF NOT EXISTS {crypto} (
                    Datetime TIMESTAMP PRIMARY KEY,
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    volume DOUBLE)
                """
                curs.execute(sql)

        self.conn.commit()

    def execute_daily(self):
        """utc 00시 00분에 가격데이터 업데이트"""

        try:  # configure 파일이 있다면 이전 업데이트 날짜 데이터를 가져오고, 최신화된 날짜인 오늘 날짜로 수정한다.
            with open('config.json', 'r') as in_file:
                config = json.load(in_file)
                dates_to_fetch = config['dates_to_fetch']

            with open('config.json', 'w') as out_file:
                config = {"dates_to_fetch": (datetime.now(timezone.utc)).strftime("%Y-%m-%d")}
                json.dump(config, out_file)

        except FileNotFoundError:  # 만약 없다면 dates_to_fetch 변수에 2년 전 날짜를 할당한 후, configure 파일을 오늘 날짜로 수정한다.
            with open('config.json', 'w') as out_file:
                dates_to_fetch = (datetime.now() - timedelta(3)).strftime("%Y-%m-%d")
                config = {"dates_to_fetch": (datetime.now(timezone.utc)).strftime("%Y-%m-%d")}
                json.dump(config, out_file)

        self.update_daily_price(dates_to_fetch)

    def update_daily_price(self, dates_to_fetch):

        def generate_date_range(start, end):
            start = datetime.strptime(start, "%Y-%m-%d")
            end = datetime.strptime(end, "%Y-%m-%d")
            for i in range(1, (end - start).days + 1):
                yield (start + timedelta(days=i)).strftime("%Y-%m-%d")

        for crypto in self.cryptos:
            for date in generate_date_range(dates_to_fetch, datetime.now().strftime("%Y-%m-%d")):
                daily_df, check = self.get_daily_crypto_data(crypto, date)
                # print(daily_df.columns())
                if check:  # 데이터가 없는 날도 존재하기 때문. ex) 상장되기 전
                    self.replace_into_db(daily_df, crypto)


    def replace_into_db(self, df, crypto):
        crypto = crypto.replace("-", "_")

        with self.conn.cursor() as curs:
            for r in df.itertuples():
                sql = "REPLACE INTO {} VALUES ('{}', {}, {}, {}, {}, {})".format(crypto, str(r.datetime),
                                                                                 r.open, r.high, r.low,
                                                                                 r.close, r.volume)
                curs.execute(sql)
            self.conn.commit()
        print("[{}] REPLACE INTO {}".format(df.datetime[0].strftime('%Y-%m-%d'), crypto))

    def get_missing_value_frame(self, df):
        day = df.index[0].strftime("%Y-%m-%d")
        next_day = self.get_next_day(day)

        temp = pd.DataFrame(pd.date_range(f'{day} 09:00:00', f'{next_day} 08:59:59', freq='1min'))\
            .rename(columns={0: "datetime"})
        df = pd.merge(left=temp, right=df, how="left", on='datetime')
        df = df.fillna(method='ffill')
        df = df.fillna(method='bfill')
        return df

    def get_next_day(self, date: str) -> str:
        tomorrow = datetime.strptime(date, '%Y-%m-%d') + timedelta(1)
        return tomorrow.strftime('%Y-%m-%d')

    def get_daily_crypto_data(self, crypto, date):
        check = False
        try:
            df = pyupbit.get_ohlcv(ticker=crypto, count=1440,
                                   to=datetime.strptime(f"{date} 9:00:00", "%Y-%m-%d %H:%M:%S"),
                                   interval="minute1")
            df['datetime'] = df.index
            df = self.get_missing_value_frame(df)
            check = True

            time.sleep(2)
            return df, check

        except Exception:
            self.logger.error(f"{crypto}의 {date} 기간 데이터가 존재하지 않습니다.")
            return None, check

    # def __del__(self):
    #     self.conn.close()

if __name__ == "__main__":
    db = DBUpdater()
    db.execute_daily()

