import pandas as pd
import pymysql
from datetime import datetime, timedelta
import mplfinance as mpf


class MarketDB:
    def __init__(self):
        """mariaDB 연결"""
        self.conn = pymysql.connect(host="",
                                    user="",
                                    password="!",
                                    db="",
                                    charset="utf8")

        self.crypto_tables = ['KRW_BTC', 'KRW_ETH', "KRW_XRP", "KRW_ADA",
                              "KRW_DOT", "KRW_DOGE", "KRW_LTC", "KRW_BCH",
                              "KRW_ETC", "KRW_ATOM", "KRW_QTUM", "KRW_TRX"]


    def __del__(self):
        """mariaDB 연결 해제"""

    def get_ohlcv_minute1(self, ticker='BTC', to=None):
        """하루 1분 캔들 데이터를 조회한다."""

        if not to:
            to = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

        from_day = datetime.strptime(to, '%Y-%m-%d') - timedelta(1)
        from_day = from_day.strftime('%Y-%m-%d')

        sql = f"SELECT * FROM {'KRW_{}'.format(ticker)} WHERE datetime >= '{from_day} 09:00:00' and datetime <= '{to} 08:59:00'"
        df = pd.read_sql(sql, self.conn)
        df = df.set_index('Datetime')

        return df

    def visualize_ohlcv(self, df):
        """데이터프레임으로 받은 데이터를 차트로 시각화한다."""

        kwargs = dict(title="OHLCV", type='candle', mav=(5, 20, 50), volume=True, ylabel='ohlc candles',
                      figratio=(25, 9))
        mc = mpf.make_marketcolors(up='r', down='b', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)

        mpf.plot(df, **kwargs, style=s)
