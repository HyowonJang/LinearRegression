Overview
---------

#### Link
[kaggle Link](https://www.kaggle.com/c/walmart-recruiting-sales-in-stormy-weather)

#### 목적
predict the sales of 111 potentially weather-sensitive products (like umbrellas, bread, and milk : around the time of major weather events at 45 of their retail locations


#### 모델의 평가기준
√ 1/n∑(log(pi+1 :-log(ai+1 : :2

n개의 상품에 대해서 log(해당 상품의 예측판매량+1 :과 log(해당 상품의 실제판매량+1 :의 잔차 제곱 평균의 제곱근을 구하여 평가한다.

##### Field descriptions
- date : 2012-01-01 ~ 2012-06-12
- store_nbr : 45개 점포
- station_nbr : 20개 기상관측소
- item_nbr : 111개 상품
- units : 일별 판매량
- id : store_nbr + item_nbr + date (ex. 2_1_2013-04-01 :

##### File descriptions

- key.csv : 점포와 기상관측소 매핑
- sampleSubmission.csv : 제출양식
- train.csv : 모든 점포 및 날짜별 판매 데이터
- test.csv - 일별 판매량을 예측해야하는 날짜, 점포, 아이템 데이터
- weather.csv : 일별 각 기상관측소의 날씨정보
- noaa_weather_qclcd_documentation.pdf : weather.csv 설명 파일

> - train.csv : date, store_nbr, item_nbr, units
> - key.csv : store_nbr, station_nbr
> - weather.csv : "station_nbr","date","tmax","tmin" ... 18개
> - test.csv : date, store_nbr, item_nbr

##### FORMAT FOR DAILY TABLE
COLUMN TERMINOLOGY
1.  DATE

Temp Degrees Fahrenheit
2. MAXIMUM (최고기온 :
3. MINIMUM (최저기온 :
4. AVERAGE (평균기온 :
5. DEPARTURE FROM NORMAL
6. AVERAGE DEW POINT (평균 이슬점 :
7. AVERAGE WET BULB (평균 습구 :

Degree Days: Base 65 F
8. HEATING (SEASON BEGINS WITH JULY :
9. COOLING (SEASON BEGINS WITH JANUARY :
10. SUNRISE (Calculated, not observed : (일출 :
11. SUNSET (Calculated, not observed : (일몰 :

Significant Weather Types Weather Phenomena
12. - +FC TORNADO/WATERSPOUT
    - FC FUNNEL CLOUD
    - TS THUNDERSTORM
    - GR HAIL
    - RA RAIN ...
