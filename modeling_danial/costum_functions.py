
"""
    포함된 함수 정보
    
    
    dateToNumeric : date컬럼을 2014-01-01의 object type에서 20140101의 int type으로 변환하는 함수.
    getStore : 원하는 지점의 정보만을 dataframe type으로 리턴한다.
    getItemInfo : 원하는 지점의 원하는 아이템의 판매정보만을 df type으로 리턴한다.
    getItemUnitsNotZero : 매출이 발생했던 아이템들 정보만을 df type으로 리턴한다.
    getItemInfoFromAllStore : 전지점에서 발생한 원하는 아이템의 매출 정보를 리턴한다.
    isThereNoneData : Missing data, Trace data의 개수정보를 받아서 만든 dataframe을 리턴한다.
    checkIsThereUnderZeroData : df의 컬럼마다 0이하에 해당하는 데이터가 몇개있는지 리턴한다.
    classifyStoresByStation : key데이터프레임을 넣어주게되면 같은 기상청을 공유하는 지점들을 따로 분할한 데이터프레임을 리턴한다.
    df_train_specified_store : 이 함수는 train df와 classifyStoresByStation를 통해 얻은 기상청마다 
            관할하는 지점들의 정보를 담은 df를 패러미터로 넣어주고, 원하는 기상청 번호를 parameter로 넣어주면 거기에 해당하는 지점들의 정보만을 리턴한다.
    divideIntoNumericAndCategoricalVariables : 컬럼을 확인해서 numerical_features와 categorical_features을 나누는 작업을 해준다.
    saveDataFrameToCsv : 넘겨준 df를 filename + 년월일시간분 의 format으로 이루어진 이름의 파일로 생성해준다.
    sendSlackDm : slack msg보내는 function
"""

from datetime import datetime
import pandas as pd
import json
import requests

# 용이한 처리를 위해 date값은 20140101 format, int 데이터 타입으로 변환
def dateToNumeric(date):
    """
        date컬럼을 2014-01-01의 object type에서 20140101의 int type으로 변환하는 함수.
        df["date"] = df["date"].apply(dateToNumeric)으로 호출하면된다.
    """
    result = ""
    li = date.split("-")
    for l in li:
        result += l
    return int(result)

def getStore(df, store_number):
    """
        원하는 지점의 정보만을 dataframe type으로 리턴한다.
        패러미터는 df, store_number를 받는다.
    """
    store = df[df["store_nbr"] == store_number].reset_index(drop=True)
    return store

def getItemInfo(df, item_num, store_number):
    """
        원하는 지점의 원하는 아이템의 판매정보만을 df type으로 리턴한다.
        패러미터는 df, item_num, store_number를 받는다.
    """
    item_n = df[df["item_nbr"] == item_num]
    item_n_sn = item_n[item_n["store_nbr"] == store_number]
    item_n_sn = item_n_sn.reset_index(drop=True)
    return item_n_sn

def getItemUnitsNotZero(df):
    """
        매출이 발생했던 아이템들 정보만을 df type으로 리턴한다.
        train dataframe만 받는다. 다른 경우는 units 컬럼이 없어서 예외처리될것.
    """
    result = df[df["units"] != 0].reset_index(drop = True)
    return result

def getItemInfoFromAllStore(df, item_num):
    """
        전지점에서 발생한 원하는 아이템의 매출 정보를 리턴한다.
        패러미터는 df, item_num을 받는다.
    """
    item_n = df[df["item_nbr"] == item_num].reset_index(drop=True)
    return item_n

def isThereNoneData(df):
    """
        Missing data, Trace data의 개수정보를 받아서 만든 dataframe을 리턴한다.
        패러미터는 df만 받는다.(weather df에서만 M, T가 존재하므로 그 외에는 의미가 없다.)
    """
    li = list(df.columns)
    m_count_li = []
    t_count_li = []
    for l in li:
        m_count = 0
        t_count = 0
        for i, contents in enumerate(df[l]):
            contents = str(contents)
            if(contents.strip() == "M"):
                m_count += 1
            if(contents.strip() == "T"):
                t_count += 1
        m_count_li.append(m_count)
        t_count_li.append(t_count)
    return pd.DataFrame({"Column" : li, "Missing Data" : m_count_li, "Trace Data" : t_count_li})

def checkIsThereUnderZeroData(df, df_columns, dtype, num_to_compare_with = 0):
    """
        df의 컬럼마다 0이하에 해당하는 데이터가 몇개있는지 리턴한다.
        용도는 M, T데이터를 우리가 어떻게 수치화할것인지 결정할 때 기준을 잡는 것이다. 
        num_to_compare_with의 default값은 0이지만, 
        num_to_compare_with의 초기값을 바꾸며 하나도 존재하지 않는 데이터를 찾아서
        M, T를 대신할 숫자를 결정하기위하여 사용하는 함수.
        
        패러미터로는 df, df_columns, dtype(str type으로 넣어준다. 예:) "int"), num_to_compare_with
        
        df_columns에는
            coulmns_should_be_integer_type_of_data을 넣거나
            coulmns_should_be_float_type_of_data을 넣어서 사용한다.
    """
    li = df_columns
    count_li = []
    for l in li:
        count = 0
        for i, contents in enumerate(df[l]):
            contents = str(contents)
            if(contents.strip() != "M" and contents.strip() != "T"):
                if(dtype == "int"):                    
                    if(int(contents) < num_to_compare_with):
                        count += 1
                if(dtype == "float"):
                    if(float(contents) < num_to_compare_with):
                        count += 1
        count_li.append(count)
    return pd.DataFrame({"Column" : li, "Under Zero" : count_li})

def classifyStoresByStation(df):
    """
        key데이터프레임을 넣어주게되면 같은 기상청을 공유하는 지점들을 따로 분할한 데이터프레임을 리턴한다.
        패러미터 df는 key.csv를 넣어준다.
    """
    dictionary = {}
    for i, station_nbr in enumerate(df["station_nbr"]):
        store_nbr = str(df["store_nbr"].loc[i])
        if station_nbr in dictionary:
            dictionary[station_nbr] += ", " + store_nbr
        else:
            dictionary[station_nbr] = store_nbr
    
    return pd.DataFrame({"station_nbr" : list(dictionary.keys()), "store_nbr" : list(dictionary.values())})

def df_train_specified_store(df, store_nbrs, station_nbr):
    """
        이 함수는 train df와 classifyStoresByStation를 통해 얻은 기상청마다 관할하는 지점들의 정보를 담은 df를 패러미터로 넣어주고,
        원하는 기상청 번호를 parameter로 넣어주면 거기에 해당하는 지점들의 정보만을 리턴한다.
    """
    store_nbrs = store_nbrs.loc[station_nbr - 1]["store_nbr"].split(", ")
    result_df = pd.DataFrame()
    for num in store_nbrs:
        num = int(num)
        if(len(result_df) == 0):
            result_df = df[df["store_nbr"] == num]
        else:
            df_temp = df[df["store_nbr"] == num]
            result_df = pd.concat([result_df, df_temp]).reset_index(drop = True)
    return result_df


def divideIntoNumericAndCategoricalVariables(df):
    """
        컬럼을 확인해서 numerical_features와 categorical_features을 나누는 작업을 해준다.
        데이터 분석하기전에 확인하면 좋은 함수. 패러미터는 df를 넣어주면 된다.
    """
    # Divide into numeric and categorical variables
    numerical_features = []
    categorical_features = []
    for f in df.columns:
    #     print(f, weather.dtypes[f])
        if df.dtypes[f] != 'object':
            numerical_features.append(f)
        else:
            categorical_features.append(f)
    print("Numerical Features Qty :", len(numerical_features),"\n")
    print("Numerical Features : ", numerical_features, "\n\n")
    print("Categorical Features Qty :", len(categorical_features),"\n")
    print("Categorical Features :", categorical_features)
    return numerical_features, categorical_features        

def saveDataFrameToCsv(df, fileName, idx = False):
    """
        넘겨준 df를 filename + 년월일시간분 의 format으로 이루어진 이름의 파일로 생성해준다.
        index를 True로 넘겨주면 저장할 때 아규먼트로 index=True를 넣어주게 된다.
    """
    fileName += "_" + datetime.now().strftime("%Y%m%d%H%M") + ".csv"
    return df.to_csv(fileName, index = idx)

def sendSlackDm(url, text):
    """
        Parameter :
            각자 받은 url을 넣어준다.
            text에는 보낼 글 내용
    """
    webhook_url = url
    slack_data = {'text': text}
    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'%(response.status_code, response.text)
    )
