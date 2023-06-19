import sqlite3
import pandas as pd
from PublicDataReader import TransactionPrice

# 데이터베이스 연결
con = sqlite3.connect("cach_data.db")

# 데이터 가져오기
service_key = "vWzA7MQ7iPgRhTfLCn8hlGdkzc9bD2HiGcNcUqay+agCCIsziNA2jr2m/hb7+fUNdeSF/iJ9DI3iMf6WYQvkJQ=="
api = TransactionPrice(service_key)

# 단일 월 조회
# 기간 내 조회
df = api.get_data(
    property_type="아파트",
    trade_type="매매",
    sigungu_code="11110",
    start_year_month="201001",
    end_year_month="202306",
)

# 데이터를 SQLite 데이터베이스에 저장
df.to_sql('cached_table', con, if_exists='replace')

# 연결 종료
con.close()
