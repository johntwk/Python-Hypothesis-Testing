import pandas as pd
import numpy as np
import re
from scipy.stats import ttest_ind
from scipy import stats

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    
    state_region = list()
    state = ""
    infile = open('university_towns.txt')
    for line in infile:
        #print(line,end="")
        line = line[:-1]
        is_state = re.search("^(.+)(\[edit\])$",line)
        if (is_state is not None):
            #state.append(is_state.group(1))
            state = is_state.group(1)
            #print("============State==============")
        else:
            if '(' in line:
                region = line[:line.index('(')-1]
                state_region.append([state,region])
                #print(region)
            else:
                region = line
                state_region.append([state,region])
    #print(state_region)
    df = pd.DataFrame( state_region, columns=["State", "RegionName"]  )
    return df
    
def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    GDP = pd.read_excel('gdplev.xls',skiprows=219)
    GDP = GDP[['1999q4', 9926.1]]
    GDP.columns = ['Quarter','GDP']
    #print(GDP)
    for i in range(2, len(GDP)):
        if (GDP.iloc[i-2][1] > GDP.iloc[i-1][1]) and (GDP.iloc[i-1][1] > GDP.iloc[i][1]):
            return GDP.iloc[i-2][0]

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    GDP = pd.read_excel('gdplev.xls', skiprows=219)
    GDP = GDP[['1999q4', 9926.1]]
    GDP.columns = ['Quarter','GDP']
    start = get_recession_start()
    start_index = GDP[GDP['Quarter'] == start].index.tolist()[0]
    GDP = GDP.iloc[start_index:]
    for i in range(2, len(GDP)):
        if (GDP.iloc[i-2][1] < GDP.iloc[i-1][1]) and (GDP.iloc[i-1][1] < GDP.iloc[i][1]):
            return GDP.iloc[i][0]

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    GDP = pd.read_excel('gdplev.xls', skiprows=219)
    GDP = GDP[['1999q4', 9926.1]]
    GDP.columns = ['Quarter','GDP']
    
    start = get_recession_start()
    start_index = GDP[GDP['Quarter'] == start].index.tolist()[0]
    end   = get_recession_end()
    end_index = GDP[GDP['Quarter'] == end].index.tolist()[0]
    
    min_val = GDP.iloc[start_index]['GDP']
    min_index = start_index
    #print(min_val)
    for i in range(start_index,end_index+1):
        #print(GDP.iloc[i]['Quarter'],":",GDP.iloc[i]['GDP']," Min: ",min_index," ",min_val)
        if (GDP.iloc[i]['GDP'] < min_val):
            min_index = i
            min_val = GDP.iloc[i]['GDP']
    return GDP.iloc[min_index]['Quarter']

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    housing = pd.read_csv("City_Zhvi_AllHomes.csv")
    housing.drop(["RegionID","Metro","CountyName","SizeRank"] , axis=1, inplace=True)
    #Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December
    #quarter_header = ["1996q2","1996q3","1996q4"] #1996-04 - 2016-08
    headers = list(housing.columns)
    headers = headers[2:11+3*12]
    housing.drop(headers,axis=1,inplace=True)
    
    quarters = []
    ym = []
    for year in range(2000,2017):
        for quarter in range(1,5):
            if (year == 2016 and quarter == 4): break
            quarters.append(str(year)+"q"+str(quarter))
    #print(quarters)

    for yq in quarters:
        quarter = yq[-1]
        year = yq[:4]
        if (quarter == "1"):
            tmp = housing[[year+"-01",year+"-02",year+"-03"]].mean(axis=1)
        if (quarter == "2"):
            tmp = housing[[year+"-04",year+"-05",year+"-06"]].mean(axis=1)
        if (quarter == "3"):
            if (year == "2016"):
              tmp = housing[[year+"-07",year+"-08"]].mean(axis=1)
            else:
              tmp = housing[[year+"-07",year+"-08",year+"-09"]].mean(axis=1)
        if (quarter == "4"):
            tmp = housing[[year+"-10",year+"-11",year+"-12"]].mean(axis=1)
        housing[yq] = tmp
    ym = []
    for year in range(2000,2017):
        for month in range(1,13):
            if (year == 2016 and month > 8): break
            if (month < 10):
                month_str = "0"+str(month)
            else:
                month_str = str(month)
            ym.append(str(year)+"-"+month_str)
    #print(ym)    
    housing.drop(ym, axis=1, inplace=1)
        #housing[quarter] = 
    housing.State.replace(to_replace=states, inplace=True)
    housing.set_index(["State","RegionName"], inplace=True)
    return housing#new_housing
 
 def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    housing = convert_housing_data_to_quarters().copy()
    #housing.reset_index(inplace = True)
    housing = housing.loc[:,'2008q3':'2009q2']
    housing.dropna()
    housing.reset_index(inplace = True)
    
    def price_ratio(row):
        return (row['2008q3'] - row['2009q2'])/row['2008q3']
    housing['diff'] = housing.apply(price_ratio,axis=1)
    uni_town = get_list_of_university_towns()
    
    uni_list = get_list_of_university_towns()
    
    def check_uni(row):
        if ((uni_list["State"] == row["State"]) & (uni_list["RegionName"] == row["RegionName"])).any():
            return 1
        else:
            return 0
    housing["is_uni"] = housing.apply(check_uni, axis = 1)
    
    u_h = housing[housing["is_uni"] == 1].dropna()['diff']
    nu_h =housing[housing["is_uni"] == 0].dropna()['diff']
    
    p_val = list(stats.ttest_ind(u_h, nu_h))[1]
    def better():
        if nu_h.mean() < u_h.mean():
            return 'non-university town'
        else:
            return 'university town'
    return (True,p_val,better())
run_ttest()
