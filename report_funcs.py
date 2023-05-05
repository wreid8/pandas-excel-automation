import string
import pandas as pd
import numpy as np
from datetime import datetime

BYTES_TO_GB = 1073741824

def get_device_count_above_threshold(df: pd.DataFrame, header: str,threshold: int) -> int:
    df[header].replace("-",np.nan, inplace=True)
    df[header] = pd.to_numeric(df[header],errors="coerce")
    return(len(df.loc[df[header] >= threshold]))

def get_G3_and_older_count(models: pd.Series) -> int:
    count = 0
    for i in models:
        if "G3" in i or "G2" in i:
            count += 1
    return count

def get_devices_count_equal_to_value(df: pd.DataFrame, header: str,value: int):
    df[header].replace("-",np.nan, inplace=True)
    df[header] = pd.to_numeric(df[header],errors="coerce")

    return(len(df.loc[df[header] == value]))

def get_devices_count_between_two_values(df: pd.DataFrame, header: str,threshold_lower: int,threshold_upper: int):
    '''
    max is inclusive, i.e a max threhold of 100 will return devices BELOW 100 \n
    min is not, i.e a min threshold of 50 will include devices equal to and above 50
    '''
    df[header].replace("-",np.nan, inplace=True)
    df[header] = pd.to_numeric(df[header],errors="coerce")

    return(len(df.loc[(df[header] < threshold_upper) & (df[header] >= threshold_lower)]))

def get_highest_value_in_column(df: pd.DataFrame, header: str):
    df[header].replace("-",np.nan, inplace=True)
    df[header] = pd.to_numeric(df[header],errors="coerce")
    max_index = df[header].idxmax()
    return df[header].max(), df._get_value(max_index,'Name')

def convert_columns_to_gb(df, headers_to_convert: list) -> pd.DataFrame:
        '''
        Converts values from a list of columns stored in a csv file from bytes to Gigabyes

        1. Creates dataframe from a csv
        2. Converts non-number values (usally "-" if exported from Nexthink) to NaN
        3. Convert all values to numeric datatype (float64)
        4. Divide by BYTES_TO_GB constant
        5. rename column names containing bytes to Gb
        returns converted dataframe
        '''

        for header in headers_to_convert:
            
            df[header].replace("-",np.nan, inplace=True)
            df[header] = pd.to_numeric(df[header])
            df[header] = df[header].div(BYTES_TO_GB,fill_value=np.nan)
            df.rename(columns={header: header.replace("bytes","Gb")},inplace=True, errors='raise')
        return df

def convert_null_to_char(df: pd.DataFrame, char:str) -> pd.DataFrame:
    '''
    prevents NaN from becoming an empty cell when exported to xlsx, char is the character to place in the empty cell.
    '''
    for column in df:
        df[column].replace(np.nan,char, inplace=True)

    return df




def remove_engine_column():
    pass

def get_worst_device_name(df: pd.DataFrame, column_name: str = ""):
    """return the device with the highest value in the given column"""
    # df_max = df.max()
    # print(df_max[column_name]) 

    #print(df.idxmax())

#CSD SPECIFIC ################

def vlookup_device_expiry(base_df: pd.DataFrame,expiry_df: pd.DataFrame):
    """insert 2 new columns for device expiry date, device EOL status"""

    expiry_df['Lease end date'] = pd.to_datetime(expiry_df['Lease end date'], unit='D', origin='1899-12-30') #convert from excel serial date to datetime object
    out_df = pd.merge(base_df, expiry_df, on='Device serial number',how='left')

    
    out_df['Is EOL'] = '-'
    #print(out_df.dtypes)
    numpy_today = np.datetime64(datetime.today())
    out_df.loc[out_df['Lease end date'] <= numpy_today, 'Is EOL'] = 'True'
    out_df.loc[out_df['Lease end date'] > numpy_today, 'Is EOL'] = 'False'
    
    #or
    #out_df.loc[out_df['Lease end date'] == np.datetime64('NaT'), 'Is EOL'] = '-' #TODO FIX THIS

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(out_df[['Lease end date','Is EOL']])
        
    out_df.insert(2, 'Lease end date', out_df.pop('Lease end date'))
    out_df.insert(3, 'Is EOL', out_df.pop('Is EOL'))
    

    return out_df


def translate_french_to_english(df: pd.DataFrame):
    """ convert Oui to Yes and Non to No on proxy table"""
    for column in df:
        df[column].replace("Oui","Yes", inplace=True)
        df[column].replace("Non","No", inplace=True)

    return df

def count_string_occurences(df: pd.DataFrame, column_name: string) -> pd.Series:
    #this will throw an error if there are 0 occurances of the given string
    return df[column_name].value_counts()
