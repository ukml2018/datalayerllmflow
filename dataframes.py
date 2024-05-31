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
        product_data_query = "SELECT manufacturer_group, product_group, product_identity, product_name FROM [dbo].[product_data_en]"
        product_data_df = pd.read_sql(sql=product_data_query, con=connection)
        r.set("product_data_df", pickle.dumps(product_data_df))
    
    ib_dataframes.append(product_data_df)

    
    #product_data_df, ff_dashboard_outlet_mapping_df, distribution_tracking_df, ff_dashboard1_df = pd.DataFrame()
       

    try:
        ff_dashboard_outlet_mapping_df = pd.DataFrame(pickle.loads(r.get("ff_dashboard_outlet_mapping_df")))
        print("ff_dashboard_outlet_mapping_df : I read from Redis.")
    
    except:
        ff_dashboard_outlet_mapping_query = "select * from ff_dashboard_outlet_mapping_en"
        ff_dashboard_outlet_mapping_df = pd.read_sql(sql=ff_dashboard_outlet_mapping_query, con=connection)
        r.set("ff_dashboard_outlet_mapping_df", pickle.dumps(ff_dashboard_outlet_mapping_df))
    
    ib_dataframes.append(ff_dashboard_outlet_mapping_df)


    try:
        ff_imperial_marketshare_outlet_df= pd.DataFrame(pickle.loads(r.get("ff_imperial_marketshare_outlet_df")))
        print("ff_imperial_marketshare_outlet_df : I read from Redis.")
    
    except:
        ff_imperial_marketshare_outlet_query = "select * from ff_imperial_marketshare_outlet_vw"
        ff_imperial_marketshare_outlet_df = pd.read_sql(sql=ff_imperial_marketshare_outlet_query, con=connection)
        r.set("ff_imperial_marketshare_outlet_df", pickle.dumps(ff_imperial_marketshare_outlet_df))
    
    ib_dataframes.append(ff_imperial_marketshare_outlet_df)

   # try:
    #    distribution_tracking_df = pd.DataFrame(pickle.loads(r.get("distribution_tracking_df")))
    #    print("distribution_tracking_df : I read from Redis.")
    
    #except:
     #   distribution_tracking_query = "select * from distribution_tracking_en"
     #   distribution_tracking_df= pd.read_sql(distribution_tracking_query,connection)
     #   r.set("distribution_tracking_df", pickle.dumps(distribution_tracking_df))
        
   # ib_dataframes.append(distribution_tracking_df)

    try:
        ff_dashboard1_df = pd.DataFrame(pickle.loads(r.get("ff_dashboard1_df")))
        print("ff_dashboard1_df : I read from Redis.")
    
    except:
        ff_dashboard1_query = "select * from ff_dashboard1_en"
        ff_dashboard1_df= pd.read_sql(ff_dashboard1_query,connection)
        r.set("ff_dashboard1_df", pickle.dumps(ff_dashboard1_df))

    ib_dataframes.append(ff_dashboard1_df)
    
    return ib_dataframes

