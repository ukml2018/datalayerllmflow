from flask import Flask, request, jsonify
import streamlit as st
from pandasai.responses.streamlit_response import StreamlitResponse
from dotenv import load_dotenv
from pandasai import exceptions as pandaex
import os
#from ibprompt import prompt_library
#from utils import rules, intent, genai_agents
from utils import intent
import dataframes

import pyarrow as pa
import redis
import pickle
import yaml
import json
app = Flask(__name__)
load_dotenv()

@app.route('/<string:userquery>', methods=['GET'])
def main(userquery):
    
    #user_query = "Find the lowest sales product from 0015I00000OYJeHQAX for cigarettes product group"
    user_query = userquery
    response = "I am not able to find answer in cache, handing over to LLM agent to generate answer"
    r= redis.StrictRedis(host="imperial-redis.redis.cache.windows.net",port=6380, password="uFSfuIjsensXBTtE8Q7JSSXiLy8GdKN0ZAzCaAuPAHo=", ssl=True)

    map_data= [{"Find Imperial market share for outlet 0015I00000OYJeHQAX":"perf_ins_1.1"},
               {"Find the market share for all product groups in the outlet 0015I00000OYJeHQAX month wise product group wise":"perf_ins_1.2"},
               {"Find market share for all SKU for Cigarettes in outlet 0015I00000OYJeHQAX month wise":"perf_ins_1.3"},
               {"Find Imperial market share for all SKU for Cigarettes in outlet 0015I00000OYJeHQAX month wise and SKU wise":"perf_ins_1.4"},
               {"Find the lowest sales product from 0015I00000OYJeHQAX for cigarettes product group":"perf_ins_1.5"},
               {"Find Imperial market share for outlet 0017S00000Aw8TpQAJ":"perf_ins_2.1"},
               {"Find the market share for all product groups in the outlet 0017S00000Aw8TpQAJ month wise product group wise":"perf_ins_2.2"},
               {"Find market share for all SKU for Cigarettes in outlet 0017S00000Aw8TpQAJ month wise":"perf_ins_2.3"},
               {"Find Imperial market share for all SKU for Cigarettes in outlet 0017S00000Aw8TpQAJ month wise and SKU wise":"perf_ins_2.4"},
               {"Find the lowest sales product from 0017S00000Aw8TpQAJ for Cigarettes product group":"perf_ins_2.5"},
               {"Find Imperial market share for outlet 0017S00000eKOdmQAG":"perf_ins_3.1"},
               {"Find the market share for all product groups in the outlet 0017S00000eKOdmQAG month wise product group wise":"perf_ins_3.2"},
               {"Find market share for all SKU for Cigarettes in outlet 0017S00000eKOdmQAG month wise":"perf_ins_3.3"},
               {"Find Imperial market share for all SKU for Cigarettes in outlet 0017S00000eKOdmQAG month wise and SKU wise":"perf_ins_3.4"},
               {"Find the lowest sales product from 0017S00000eKOdmQAG for cigarettes product group":"perf_ins_3.5"},
               {"Find Imperial market share for outlet 0017S00000eKOdZQAW":"perf_ins_4.1"},
               {"Find the market share for all product groups in the outlet 0017S00000eKOdZQAW month wise product group wise":"perf_ins_4.2"},
               {"Find market share for all SKU for Cigarettes in outlet 0017S00000eKOdZQAW month wise":"perf_ins_4.3"},
               {"Find Imperial market share for all SKU for Cigarettes in outlet 0017S00000eKOdZQAW month wise and SKU wise":"perf_ins_4.4"},
               {"Find the lowest sales product from 0017S00000eKOdZQAW for cigarettes product group":"perf_ins_4.5"},
               {"Find Imperial market share for outlet 0017S00000lexgKQAQ":"perf_ins_5.1"},
               {"Find the market share for all product groups in the outlet 0017S00000lexgKQAQ month wise product group wise":"perf_ins_5.2"},
               {"Find market share for all SKU for Cigarettes in outlet 0017S00000lexgKQAQ month wise":"perf_ins_5.3"},
               {"Find Imperial market share for all SKU for Cigarettes in outlet 0017S00000lexgKQAQ month wise and SKU wise":"perf_ins_5.4"},
               {"Find the lowest sales product from 0017S00000lexgKQAQ for cigarettes product group":"perf_ins_5.5"},
               ]
   
   
    key = ""
    for insight in map_data:
        if list(insight.keys())[0] == user_query:
            key = list(insight.values())[0]
            break
    
    if key:
        try:
            response = pickle.loads(r.get(key))
            print("I got the response in cache")
        except:
            print("I didn't get the response in cache. I will call LLM agent now.") 
        try:
            response=call_llm_agent(user_query)
            print("I will add the response to cache now") 
            r.set(key, pickle.dumps(response))
        except:
            print("I didn't get the response in llm model. I will call LLM agent now.") 

    else:
        try:
          print("Before calling LLm agent")
          response=call_llm_agent(user_query)
        except:
          print("I didn't get the response in llm model. I will call LLM agent now.") 

    print(response)    
    return json.dumps(response)

##@app.route('/agent/<user_query>', methods=['GET'])
def call_llm_agent(user_query: str):

    #st.set_page_config(page_title = "PandasAI",page_icon = "🐼")
    #st.title("Chat with Your Data using PandasAI:🐼")

    #with st.sidebar:
        #st.title("Configuration:⚙️")

    user_query = user_query
    
    rule_set = intent.ll_helper_rules()
    added_new_rule = intent.need_update()

    if rule_set:
        intent_vector = intent.create_vector(rules= rule_set, new_rule_added=added_new_rule)
        response = intent.get_intent(query=user_query, vectordb=intent_vector)
        document = response[0][0]
        similarity_score = response[0][1]
        print(document.page_content)
        print(similarity_score)
    
        if similarity_score*100 > 70.0:
            ll_prompt = intent.get_simple_ib_prompt() + "\n" + document.page_content + "\n Now, "+ user_query
        else:
            ll_prompt = intent.get_simple_ib_prompt() + "\n" + user_query   
    else:
        ll_prompt = intent.get_simple_ib_prompt() + "\n" + user_query   
    
    print(ll_prompt)

    connection = dataframes.connect_to_database()
    ibm_dataframes = dataframes.create_dataframes(connection)

    ib_datalake = intent.create_panda_smartdatalake(ibm_dataframes)

    #MAX_RETRY_COUNT = 2
    #retry_count = 0
    success_flag = True

    #while retry_count <  MAX_RETRY_COUNT:
        
    try:
        response = ib_datalake.chat(ll_prompt)
        if 'Unfortunately, I was not able to answer your question' in str(response):
            print("Response with exception:")
            print(response)
            raise pandaex.NoCodeFoundError      
    except:
        #retry_count = retry_count+1
        print("Custom : An exception occured while generating Datalake LLM response.")
        success_flag = False

    try:
        d = response.to_dict(orient='records')
        output = json.dumps(d)
    
    except:
        output = response
    
    print(response)
    print("This is JSON:")
    print(output)
    print(success_flag)
    #print("Retry Count :" + str(retry_count))

    return output 

if __name__ == '__main__':
    app.run(debug=True,port=8888)
   
