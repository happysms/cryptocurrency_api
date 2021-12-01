# cryptocurrency_api

## 설명
- 용도: 백테스팅(시뮬레이션)을 위한 분 단위 암호화폐 과거 데이터 추출

- 배경
  - 투자 알고리즘을 조금이라도 더 정확하게 백테스팅하기 위해서는 짧은 단위(ex 분 단위)의 데이터가 필요하다. 물론 거래소 API를 통해 과거 데이터를 추출할 수 있다. 하지만 여기에는 두 가지 문제점이 존재한다.
  
    - **첫번째**, 거래소 API는 호출 제한이 있다. 대량의 데이터를 무수히 요청할 때 주기적으로 프로그램을 일시정지를 시켜야 하기 때문에 시간이 매우 오래 걸린다. 
    
    - **두번째**, 짧은 단위의 데이터는 누락된 데이터가 굉장히 많다. 이는 백테스팅 코드를 작성할 때 커다란 영향을 준다.

-------------------------------

## 구현 방식

1. **AWS RDS로 DB인스턴스 생성**
  - 어느 환경에서든 upbit api처럼 호출할 수 있도록 클라우드 환경에서 데이터베이스를 구축한다.
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144251209-26889113-b51a-4fed-800d-14722cf36dbb.png" class="center" width="800" height="100" /></p>

2. **데이터베이스 생성 및 업데이트를 수행하는 코드 구현**
  - 업비트 상장 기준 암호화폐 시가 총액 상위 6개 종목(BTC, ETH, XRP, DOGE, ADA, DOT)의 2년 간의 1분 봉 데이터를 저장한다.

  - 프로그램을 처음 실행시키는 경우에는 config.json 파일을 생성하여 오늘 날짜를 기록합니다. 그리고 오늘부터 2년 전까지의 데이터를 불러온다.

  - 만약 처음 프로그램을 실행하지 않았다면 config.json 파일에 기록된 마지막 업데이트 날짜를 가져와 해당 날짜부터 오늘까지의 데이터를 DB에 업데이트한다.

<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144251835-d8c59a65-1537-47b6-9f97-09c382a8d8d7.png" class="center" width="600" height="300" /></p>

  - 아래의 방식대로 DB에 데이터를 업데이트한다. 다만 해당 날짜가 해당 코인의 상장 이전이라면 데이터가 없기에 이를 체크하는 코드도 추가했다.
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144253031-b47836f6-982b-4a5d-99d3-af69fcacab06.png" class="center" width="800" height="100" /></p>

  - 아래의 방식대로 결측 값을 채운다.
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144253452-6a248331-43af-40bf-9574-f8992255aebb.png" class="center" width="750" height="500" /></p>

  - 데이터가 너무 많아질 것을 우려하여 2년치 데이터량을 넘어서면 하루치를 삭제한다.
  ```python 
  with self.conn.cursor() as curs:
            for crypto in self.crypto_tables:
                sql = f"SELECT COUNT(*) FROM {crypto}"
                curs.execute(sql)
                result = curs.fetchall()

                if result[0][0] > 1051200:  # 730(2년) * 1440 = 1051200
                    sql = f'select MIN(datetime) from {crypto}'
                    curs.execute(sql)

                    result = curs.fetchall()
                    day = result[0][0].strftime("%Y-%m-%d")
                    next_day = self.get_next_day(day)

                    sql = f"delete from {crypto} where datetime >= '{day} 09:00:00' and datetime <= '{next_day} 08:59:00'"
                    curs.execute(sql)

            self.conn.commit()
  
  ```

3. **AWS Lambda를 활용하여 매일 1회 함수를 작동시켜 데이터베이스를 업데이트 & 도커 사용**
  - 람다에 코드를 올리기에는 패키지 파일의 용량이 크기 때문에 도커를 활용해서 배포했다. (판다스 패키지가 용량이 조큼 큼.) AWS ECR에 이미지를 등록하여 사용.
  
  - 매일 UTC 기준 00시 10분에 함수를 실행하도록 CloudWatch Event를 트리거했다.
  
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144254311-fc869e02-775a-44b3-893f-757914744fbb.png" class="center" width="600" height="200" /></p>

4. **API 사용법**
  - 특정 종목의 특정 날짜의 분봉 데이터를 조회할 수 있다.

<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144254768-5dea6f75-7c42-4922-bf76-4ce60c634cd1.png" class="center" width="470" height="400" /></p>

  - 데이터를 차트로 시각화 한다.

<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144255154-0269c2a9-8b91-4adc-b475-0d6de6a99fca.png" class="center" width="700" height="400" /></p>

## 사용 기술 스택
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144255602-17a5309b-8a65-459f-85a2-25df8bb3080c.png" class="center" width="600" height="300" /></p>

