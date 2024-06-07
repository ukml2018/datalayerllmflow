from pandasai import SmartDataframe
import pandas as pd

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
import urllib.parse
import pyodbc

import redis
#import pyarrow as pa
import pickle

def connect_to_database():
    server = "ib-azure-sql.database.windows.net"
    database = "ImperialBrands"
    username = "sqladmin"
    password = "Admin#123"

    driver = '{ODBC Driver 17 for SQL Server}'
    #driver   = 'Driver={odbc_driver}'

    odbc_str = 'DRIVER='+driver+';SERVER='+server+';PORT=1433;UID='+username+';DATABASE='+ database + ';PWD='+ password
    connection = pyodbc.connect(odbc_str)
    #connect_str = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(odbc_str)
    #print(connect_str)
    return connection


def create_dataframes(connection):

    r= redis.StrictRedis(host="imperial-redis.redis.cache.windows.net",port=6380, password="uFSfuIjsensXBTtE8Q7JSSXiLy8GdKN0ZAzCaAuPAHo=", ssl=True) 
    ib_dataframes: list[pd.DataFrame] = []


    try:
        product_data_df = pd.DataFrame(pickle.loads(r.get("product_data_df")))
        print("product_data_df : I read from Redis.")
    
    except:
        print("Unable to load datafames from cache")
        product_data_query = "SELECT manufacturer_group, product_group, product_identity, product_name FROM product_data_en"
        product_data_df = pd.read_sql(sql=product_data_query, con=connection)
        r.set("product_data_df", pickle.dumps(product_data_df))
        print("Loaded to Redis.")
    
    ib_dataframes.append(product_data_df)

    #try:
        #ff_dashboard1_df = pd.DataFrame(pickle.loads(r.get("ff_dashboard1_df")))
        #print("ff_dashboard1_df : I read from Redis.")
    
    #except:
        #ff_dashboard1_query = "select * from ff_dashboard1_en"
        #ff_dashboard1_df= pd.read_sql(ff_dashboard1_query,connection)
        #r.set("ff_dashboard1_df", pickle.dumps(ff_dashboard1_df))
    
    #ib_dataframes.append(ff_dashboard1_df)
          

    try:
        ff_dashboard_outlet_mapping_df = pd.DataFrame(pickle.loads(r.get("ff_dashboard_outlet_mapping_df")))
        print("ff_dashboard_outlet_mapping_df : I read from Redis.")
    
    except:
        ff_dashboard_outlet_mapping_query = "select outlet_id, outlet_address, customer_number, area_code, region_code, micro_region_desc from ff_dashboard_outlet_mapping_en"
        ff_dashboard_outlet_mapping_df = pd.read_sql(sql=ff_dashboard_outlet_mapping_query, con=connection)
        r.set("ff_dashboard_outlet_mapping_df", pickle.dumps(ff_dashboard_outlet_mapping_df))
        print("Loaded to Redis.")
    
    ib_dataframes.append(ff_dashboard_outlet_mapping_df)


    try:
        reconnect_export_df = pd.DataFrame(pickle.loads(r.get("reconnect_export_df")))
        print("reconnect_export_df : I read from Redis.")
    
    except:
        print("Reloading the table to cache.....")
        reconnect_export_query = "select product_identity, region, outlet_id, transaction_date, measure_sales_volume, product_group, product_type, region_code from reconnect_export_en"
        reconnect_export_df = pd.read_sql(sql=reconnect_export_query, con=connection)
        r.set("reconnect_export_df", pickle.dumps(reconnect_export_df))
        print("Loaded to Redis.")
    
    ib_dataframes.append(reconnect_export_df)

    try:
        rc_outlet_marketshare_vw_df= pd.DataFrame(pickle.loads(r.get("rc_outlet_marketshare_vw_df")))
        print("rc_outlet_marketshare_vw_df : I read from Redis.")
    
    except:
        rc_outlet_marketshare_vw_query = "select * from rc_outlet_marketshare_vw"
        rc_outlet_marketshare_vw_df = pd.read_sql(sql=rc_outlet_marketshare_vw_query, con=connection)
        r.set("rc_outlet_marketshare_vw_df", pickle.dumps(rc_outlet_marketshare_vw_df))
        print("Loaded to Redis.")
    
    ib_dataframes.append(rc_outlet_marketshare_vw_df)

    try:
        distribution_tracking_df = pd.DataFrame(pickle.loads(r.get("distribution_tracking_df")))
        print("distribution_tracking_df : I read from Redis.")
    
    except:
        print("Let's reload the table again to cache:")
        distribution_tracking_query = "SELECT outlet_id, product_identity, product_desc, product_in_stock, product_out_of_stock, micro_region FROM distribution_tracking_en"
        distribution_tracking_df= pd.read_sql(distribution_tracking_query,connection)
        r.set("distribution_tracking_df", pickle.dumps(distribution_tracking_df))
        print("Loaded to Redis.")
        
    ib_dataframes.append(distribution_tracking_df)
    
    connection.close()
    
    return ib_dataframes
