
from time import strftime
import pandas as pd
import numpy as np
from datetime import datetime

from report_funcs import *

input_path = r"input/csd data.xlsx" #the input path for the csv
lease_data_path = r"lease-data.xlsb"

def base_data_report(df_base: pd.DataFrame, df_net: pd.DataFrame):
    
    
    ''' this functions takes the data pulled from the base data csv, and returns a full report'''
    #base data:
    device_count_total = len(df_base.index)
    device_count_8gb = len(df_base.loc[df_base['Total RAM [Gb]'] == 8.0])
    device_count_g3_or_older = get_G3_and_older_count(df_base["Device model"])
    device_count_slow_boot = get_device_count_above_threshold(df_base,"Average boot duration [s]", 120)
    device_count_slow_extended_logon = get_device_count_above_threshold(df_base,"Average extended logon duration [s]", 300)
    device_count_100_percent_high_mem_time = get_devices_count_equal_to_value(df_base,"High device memory time ratio [%]",100)
    device_count_between_50_and_100_percent_high_mem_time = get_devices_count_between_two_values(df_base,"High device memory time ratio [%]",50,100)
    highest_cpu, highest_cpu_device = get_highest_value_in_column(df_base,"High device overall CPU time ratio [%]")
    most_app_crash_device_crash_count, most_app_crash_device = get_highest_value_in_column(df_base,"Number of application crashes")
    device_count_over_10_app_crashes = get_device_count_above_threshold(df_base,"Number of application crashes",11)

    #network data:
    device_count_less_than_50_percent_connection_ratio = get_devices_count_between_two_values(df_base,"Successful network connections ratio [%]",0,50)
    device_count_between_50_and_75_percent_connection_ratio = get_devices_count_between_two_values(df_base,"Successful network connections ratio [%]",50,75)
    device_count_over_100ms_response_time = get_device_count_above_threshold(df_net,"Average network response time [ms]",100)

    # WARNING !!!!! : this will throw an error if there are 0 occurances of the string
    eol_series = count_string_occurences(df_base,'Is EOL')
    
    
    email_date = strftime("%d") + "-" + strftime("%m")
    output = f"""

    Weekly Data Pull & Short Analysis - CSD {email_date}

    In the past week Nexthink saw {device_count_total} devices

    Of those {device_count_total}:

    Asset Management: 
    •   Devices not due for replacement (since purchase): {eol_series['False']}
    •   Devices overdue for replacement (since purchase): {eol_series['True']}
    •   Unknown: {eol_series['-']}  

    Network: 
    •	{device_count_less_than_50_percent_connection_ratio} devices had a less than 50% successful connection ratio
    •	{device_count_between_50_and_75_percent_connection_ratio} devices have between 50% and 75% successful connection ratio
    •	{device_count_over_100ms_response_time} devices have over 100ms average network response rate     

    Hardware:
    •	{device_count_8gb} device(s) have 8GB of RAM 
    •	{device_count_g3_or_older} devices are a G3 model or older
    
    Performance:
    •	{device_count_slow_boot} devices take longer than 2 minutes to boot 
    •	{device_count_slow_extended_logon} devices take longer than 5 minutes to complete extended logon (device ready to use)
    •	{device_count_100_percent_high_mem_time} devices are spending 100% of their time at high memory usage
    •	{device_count_between_50_and_100_percent_high_mem_time} devices spend between 50% and 100% of their time at high memory usage 
    •	The worst performing device by CPU usage ({highest_cpu_device}), spent {highest_cpu}% of its time at high CPU usage
    •	The device with the most app crashes ({most_app_crash_device}), had {most_app_crash_device_crash_count} application crashes over the 7 day period
    •	{device_count_over_10_app_crashes} devices had over 10 app crashes
    """
    return output

    
def main(debug=False):
    ''' 
    Preparing a file for this script:
    1. run investigations in nexthink
    2. save spreadsheet in input folder, sheet should have 5 pages, BASE data, Network data, proxy data, SIP endpoint data and Neo data.
    '''

    #TODO: automate tagging of devices, gettign data form NT

    print("\n\n\n")

    print("Importing report data...")

    df_base = pd.read_excel(input_path, sheet_name=0,dtype=object)
    df_net = pd.read_excel(input_path, sheet_name=1,dtype=object) #change to read_csv in future when i can get data with API
    df_proxy = pd.read_excel(input_path, sheet_name=2,dtype=object)
    df_sip = pd.read_excel(input_path, sheet_name=3,dtype=object)
    df_neo = pd.read_excel(input_path, sheet_name=4,dtype=object)

    print("Importing lease data...")
    df_lease_data = pd.read_excel(lease_data_path)

    print("Converting to Gigabytes...")
    #convert all bytes columns to gigabytes:
    df_base_converted = convert_columns_to_gb(df_base,[
        "Total RAM [bytes]",
        "System drive free space [bytes]",
        "Total network traffic [bytes]"])
    df_net_converted = convert_columns_to_gb(df_net,[
        "Total network traffic [bytes]",
        "Incoming network traffic [bytes]",
        "Outgoing network traffic [bytes]",
        "Total web traffic [bytes]",
        "Incoming web traffic [bytes]",
        "Outgoing web traffic [bytes]"])

    df_sip_converted = convert_columns_to_gb(df_sip,[
        "Total network traffic [bytes]",
        "Incoming network traffic [bytes]",
        "Outgoing network traffic [bytes]"])

    df_neo_converted = convert_columns_to_gb(df_neo,[
        "Total network traffic [bytes]",
        "Incoming network traffic [bytes]",
        "Outgoing network traffic [bytes]"])

     # translate french to english
    df_proxy_translated = translate_french_to_english(df_proxy)

    print("Performing lease end date vlookup...")
    # add aditional data columns for expiry dates (SPECIFIC TO CSD DO NOT DO FOR ANY OTHER BU)
    df_base_converted_with_expiry_dates = vlookup_device_expiry(df_base_converted, df_lease_data)
    
    #drop all engine columns
    df_base_converted_with_expiry_dates.drop(['Engine'], axis='columns', inplace=True)
    df_net_converted.drop(['Engine'], axis='columns', inplace=True)
    df_proxy_translated.drop(['Engine'], axis='columns', inplace=True)
    df_sip_converted.drop(['Engine'], axis='columns', inplace=True)
    df_neo_converted.drop(['Engine'], axis='columns', inplace=True)
    
    get_worst_device_name(df_base_converted_with_expiry_dates,"Number of application crashes")
    
    
    #write formatted report to excel document and name accordingly
    date = datetime.now()
    with pd.ExcelWriter(fr'output/CSD Base Data {date.year}-{date.month}-{date.day}.xlsx') as writer:
        # Write each dataframe to a different worksheet.
        convert_null_to_char(df_base_converted_with_expiry_dates,"-").to_excel(writer, sheet_name='Base', index=False)
        convert_null_to_char(df_net_converted,"-").to_excel(writer, sheet_name='Net',index=False)
        df_proxy_translated.to_excel(writer, sheet_name='Proxy',index=False)
        convert_null_to_char(df_sip_converted,"-").to_excel(writer, sheet_name='SIPEndpoint',index=False)
        convert_null_to_char(df_neo_converted,"-").to_excel(writer, sheet_name='NEO',index=False)

    #### OUTPUT THE FINAL REPORT ###
    
    report = base_data_report(df_base_converted_with_expiry_dates,df_net_converted)
    
    if debug == False:
        print(report)
    
    return report
    #################################


