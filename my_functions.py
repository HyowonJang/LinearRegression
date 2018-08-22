from datetime import datetime
import pandas as pd
import json
import requests
import numpy as np
import scipy as sp
from dateutil.parser import parse

def isThereNoneData(df, percentage=60):
    """
        Missing data, Trace data, - data의 개수정보를 받아서 만든 dataframe을 리턴한다.
        패러미터는 df와, 상기된 데이터들이 해당 컬럼에서 차지한 percentage정도를 출력하고싶을때 입력한다. 
        default는 60% 이상인 컬럼명을 출력한다.
    """
    columns = ["Column", "Row Count", "Missing Data", "M Data %", "Trace Data", "T Data %", "Bar Data", "B Data %"]
    li = list(df.columns)
    m_count_li = []
    t_count_li = []
    b_count_li = []    
    row_count_li = []
    m_percent_li = []
    t_percent_li = []
    b_percent_li = []
    for l in li:
        m_count = 0
        t_count = 0
        b_count = 0
        for i, contents in enumerate(df[l]):
            contents = str(contents)
            if(contents.strip() == "M"):
                m_count += 1
            if(contents.strip() == "T"):
                t_count += 1
            if(contents.strip() == "-"):
                b_count += 1            
        m_count_li.append(m_count)
        t_count_li.append(t_count)
        b_count_li.append(b_count)
        row_count_li.append(len(df[l]))
        m_percent_li.append(round(m_count/len(df[l])*100, 2))
        t_percent_li.append(round(t_count/len(df[l])*100, 2))
        b_percent_li.append(round(b_count/len(df[l])*100, 2))
    result_df = pd.DataFrame({
        "Column" : li, 
        "Row Count" : row_count_li,
        "Missing Data" : m_count_li, 
        "M Data %" : m_percent_li,
        "Trace Data" : t_count_li, 
        "T Data %": t_percent_li,
        "Bar Data" : b_count_li, 
        "B Data %" : b_percent_li}, 
         columns=columns) 
    
    for column in ["M Data %", "T Data %", "B Data %"]:
        print("{} over {}% : {}".format(" ".join(column.split(" ")[:-1]), \
                                        percentage, list(result_df["Column"][result_df[column] >= percentage])))
    return result_df

def changeTypeToInt(a):
    temp = str(a).strip()
    if temp == 'M' or temp == '-':
        return np.nan
    else:
        return int(a)
    
def changeTypeToFloat(a):
    temp = str(a).strip()
    if temp == 'M' or temp == '-':
        return np.nan
    elif temp == 'T':
        return 0
    else:
        return float(a)
    
def changeTypes(df, columns = [], print_msg = True):
    result_df = df.copy()
    if len(columns) == 0:
        columns = result_df.columns
    cols_int = ["tmax", "tmin", "tavg", "dewpoint", "wetbulb", "heat", "cool", "sunrise", "sunset"]
    cols_float = ["snowfall", "preciptotal", "stnpressure", "sealevel", "depart", "resultspeed", "resultdir", "avgspeed"]
    
    process_int = []
    process_float = []
    for column in columns:
        if column in cols_int:
            process_int.append(column)
            result_df[column] = result_df[column].apply(changeTypeToInt)
        elif column in cols_float:
            process_float.append(column)
            result_df[column] = result_df[column].apply(changeTypeToFloat)

#     result_df = result_df.dropna()

#     if print_msg:
#         print("원본 데이터프레임 length : " + str(len(df)))
#         print("제거하고 싶은 컬럼 : " + str(list(columns)))
#         print("제거한 int 컬럼 : " + str(process_int))
#         print("제거한 float 컬럼 : " + str(process_float))
#         print("제거한 후 데이터프레임 length : " + str(len(result_df)))
        
    return result_df

def remove_columns(df, columns = [], print_msg = True):
    """
        data_frame 파일을 df 패러미터로 넣어준다.
        columns에 제거하고싶은 columns를 리스트형식으로 넣어준다.
    """
    for column in columns:
        df.drop(column, axis=1, inplace=True)
        
    if print_msg:
        print("제거한 컬럼명 : " + str(list(columns)))
        
    return df.tail()

def divideIntoNumericAndCategoricalVariables(df):
    """
        컬럼을 확인해서 numerical_features와 categorical_features을 나누는 작업을 해준다.
        데이터 분석하기전에 확인하면 좋은 함수. 패러미터는 df를 넣어주면 된다.
    """
    numerical_features = []
    categorical_features = []
    for f in df.columns:
        if df.dtypes[f] != 'object' and f != "station_nbr":
            numerical_features.append(f)
        else:
            if f != "date":
                categorical_features.append(f)
    print("Numerical Features Qty :", len(numerical_features),"\n")
    print("Numerical Features : ", numerical_features, "\n\n")
    print("Categorical Features Qty :", len(categorical_features),"\n")
    print("Categorical Features :", categorical_features)
    return numerical_features, categorical_features

def getStoreList(df, item_nbr, msg=True):
    df_ = df.copy()
    df_ = df_[df_["item_nbr"] == item_nbr]
    df_ = df_[df_["units"] != 0]
#     if msg:
#         print("팔린 개수가 0이상인 row 개수 : " + str(len(df_)))
#         print("총 팔린 개수 : " + str(df_["units"].sum()))
#         print(str(item_nbr) + "번 아이템이 팔린 스토어 개수 : " + str(len(list(df_["store_nbr"].unique()))))
#         print(str(item_nbr) + "번 아이템이 팔린 스토어 넘버 리스트 : " + str(list(df_["store_nbr"].unique())))
#     return list(df_["store_nbr"].unique())
    return len(list(df_["store_nbr"].unique()))

def report_item_sales(df):
    item_nbr_li = df["item_nbr"].unique()
    y_li = []
    for item_nbr in item_nbr_li:
        y_li.append(getStoreList(df, item_nbr))
    return item_nbr_li, y_li

def setAnnotateLocation(idx_li):
    result = []
    base_loc = (-8, 10)
    up_loc = (-8, 25)
    check_li = [22, 38, 83, 96]
    for i, idx in enumerate(idx_li):
        if idx in check_li:
            result.append(up_loc)
        else:
            result.append(base_loc)
        tmp = idx
    return result

def to_nan(a):
    temp = str(a).strip()
    if temp == 'M' or temp == '-':
        return np.nan
    elif temp == "T":
        return 0
    else:
        return float(a)
    
def nan_to_zero(a):
    if np.isnan(a):
        return 0
    else:
        return 1

def sum_missing_values(data):
    return len(data) - np.sum(data)    
    
def returnWeatherMissingValueDataByStation(df_):
    df = df_.copy()
    weather_columns = ['tmax', 'tmin', 'tavg', 'depart', 'dewpoint', 'wetbulb', 'heat', 'cool', 'sunrise', 'sunset','snowfall', 'preciptotal', 'stnpressure', 'sealevel', 'resultspeed', 'resultdir', 'avgspeed']
    for column in weather_columns:
        df[column] = df[column].apply(to_nan)
        df[column] = df[column].apply(nan_to_zero)
        
    return df.pivot_table(weather_columns, "station_nbr", aggfunc=sum_missing_values)

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

def getCodesumUniqueDataList(codesum):
    codesums = str(codesum).strip().split(" ")
    for cd in codesums:
        if cd != "":
            if len(cd) > 3:
                if cd[:2] == format_d:
                    return 1
                if cd[2:] == format_d:
                    return 1
            else:   
                if cd == format_d:
                    return 1
        else:
            return 0

def getCodesumUniqueDataList(df):
    df_codesum = df["codesum"]
    codesum_data_list = []
    for codesum in df_codesum:
        codesum = str(codesum).strip()
        cds = codesum.split(" ")
        if len(cds) != 0:
            for cd in cds:
                if cd != "":
                    if len(cd) > 3:
                        if cd[:2] not in codesum_data_list:
                            codesum_data_list.append(cd[:2])
                        if cd[2:] not in codesum_data_list:
                            codesum_data_list.append(cd[2:])
                    else:   
                        if cd not in codesum_data_list:
                            codesum_data_list.append(cd)
    return codesum_data_list

def setCodesumUniqueDataList(codesum):
    codesums = str(codesum).strip().split(" ")
    
    for cd in codesums:
        if cd != "":
            if len(cd) > 3:
                if cd[:2] == format_d:
                    return 1
                if cd[2:] == format_d:
                    return 1
            else:   
                if cd == format_d:
                    return 1
        else:
            return 0
        
def getCodesumFormats():
    codesum_formats = [
     "Rain", "Freezing", "Fog", "Mist", "Unknown Precipitation",\
     "HeavyFog", "Shallow", "Snow", "Haze", "ThunderStorm", "Vicinity",\
     "Drizzle", "Blowing", "Patches", "Widespread Dust", "Squall", "Ice Pellets",\
     "Smoke", "Hail", "Small Hail or Snow Pellets", "Snow Grains", "Partial", "Moderate"
    ]
    return codesum_formats

def getIndependentTwoSampleTest(df, codesum_list, df_moderate):
    result_li = []
    for codesum in codesum_list:
        df_ = df[df[codesum] != 0]
        day_length = len(df_)
        statistic , p_value = sp.stats.ttest_ind(df_["units"], df_moderate["units"], equal_var = False)
        if p_value <= 0.01:
            print(codesum_dict[codesum], codesum_num[codesum])
            print(round(p_value, 5))

def handle_date_Y(a):
    return parse(a).year

def handle_date_M(a):
    return parse(a).month

def handle_date_D(a):
    return parse(a).day
            
def isnan(a):
    if np.isnan(a):
        return 0
    else:
        return 1
    
def getSpecifiedWeatherData(df, station_nbr):
    """
        df와 station_nbr를 받는다.
    """
    return df[df["station_nbr"] == station_nbr].reset_index(drop=True)

def saveDataFrameToCsv(df, fileName, idx = False):
    """
        넘겨준 df를 filename + 년월일시간분 의 format으로 이루어진 이름의 파일로 생성해준다.
        index를 True로 넘겨주면 저장할 때 아규먼트로 index=True를 넣어주게 된다.
    """
    fileName += "_" + datetime.now().strftime("%Y%m%d%H%M") + ".csv"
    return df.to_csv(fileName, index = idx)