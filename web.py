import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pandas as pd
import statsmodels.api as sm

app = Flask(__name__)

# 아파트 실거래가 조회 페이지
@app.route('/')
def home():
    return render_template('index.html')

# 검색 결과 및 예측 페이지
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        # 데이터베이스 연결
        con = sqlite3.connect("cached_data.db")
        cursor = con.cursor()

        # 사용자가 입력한 값 가져오기
        district = request.form.get('법정동')
        apartment = request.form.get('아파트')

        # 입력값이 비어있는지 확인
        if not (district and apartment):
            return redirect(url_for('home'))
        

        # 데이터베이스에서 필터링된 결과 가져오기
        query = "SELECT 년, 월, 층, 거래금액, 전용면적 FROM cached_table WHERE 법정동 LIKE ? AND 아파트 LIKE ? ORDER BY 년 DESC, 월 DESC"
        params = ('%' + district + '%', '%' + apartment + '%')
        cursor.execute(query, params)

        # 결과 가져오기
        results = cursor.fetchall()

        # 데이터베이스 연결 종료
        cursor.close()
        con.close()

        # 검색 결과를 result.html에 전달하여 표시
        return render_template('result.html', results=results)

    else:
        # GET 요청에 대해 index.html을 반환
        return render_template('index.html')


# 예측 페이지
@app.route('/prediction', methods=['POST', 'GET'])
def prediction():
    if request.method == 'POST':
        # 저장된 데이터 가져오기
        con = sqlite3.connect("cached_data.db")
        cursor = con.cursor()

        # 사용자가 입력한 값 가져오기
        district = request.form.get('법정동')
        apartment = request.form.get('아파트')

        # 데이터베이스에서 필터링된 결과 가져오기
        query = "SELECT 년, 월, 층, 거래금액, 전용면적 FROM cached_table WHERE 법정동 LIKE ? AND 아파트 LIKE ? ORDER BY 년 DESC, 월 DESC"
        params = ('%' + district + '%', '%' + apartment + '%')
        cursor.execute(query, params)

        # 결과 가져오기
        results = cursor.fetchall()

        # 저장된 데이터 가져오기
        df = pd.DataFrame(results, columns=['년', '월', '층', '거래금액', '전용면적'])
        df['면적당금액'] = df['거래금액'] / df['전용면적']
        predicted_year = int(request.form.get('predicted_year'))
        predicted_month = int(request.form.get('predicted_month'))

    
        # Regression analysis
        X = df[['년', '월']]
        y = df['면적당금액']
        X = sm.add_constant(X)
        model = sm.OLS(y, X)
        results = model.fit()


        new_data = pd.DataFrame({
            'const': 1,
            '년': [predicted_year],
            '월': [predicted_month]
        })
        new_data = sm.add_constant(new_data)
        predicted_price_per_area = results.predict(new_data)
        predicted_price_per_unit = round(predicted_price_per_area[0], 2)


        # 예측 결과를 prediction.html에 전달하여 표시
        return render_template('prediction.html', predicted_price_per_unit=predicted_price_per_unit)

    else:
        # GET 요청에 대해 index.html을 반환
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
