from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
#import llmlibrary
import os
import sys


from pandasai import SmartDatalake
import pandas as pd
from pandasai.responses.streamlit_response import StreamlitResponse


from langchain_openai import AzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.chat_models import AzureChatOpenAI



def need_update():
        
        NEW_RULE_ADDED = False
        return NEW_RULE_ADDED

def ll_helper_rules():

    rules = list()
    rules.append("To calculate total Imperial sale per region, follow the steps: 1. Find all the products which are manufactured by Imperial. 2. Find region code and sales volume for those products. 3. Then generate the total sale volume per region.")
    rules.append("To Calculate Market Share for a region, follow these steps: 1. Calculate total sales volume for all regions; 2. Calculate sales volume for the particular region in question; 3. Percentage market share is Total sale of the region divided by Total sale multiply by 100.")
    rules.append("To calculate Imperial Market Share for an outlet, look at imperial_marketshare_outlet dataset ")
    rules.append("To calculate Market Share for a product in an outlet, follow these steps: 1. Calculate total sales volume for that product group in the outlet; 2. calculate sales volume for Imperial for that particular product group in that outlet; 3. Percentage market share is the total Imperial sale of the product group in that outlet divided by Total sale for the product group in the outlet multiply by 100.")
    rules.append("To calculate Imperial Market Share for a product in an outlet, follow these steps: 1. Calculate total sales volume in the outlet; 2. calculate sales volume for the product group in that outlet; 3. Percentage market share is the total sale of the product group in that outlet divided by Total sale of the outlet multiply by 100.")
    rules.append("To Calculate market share for all SKU for a product category in an outlet, follow these steps: 1. Find all the SKU fo the product category sold in the outlet; 2. Then find those SKU sales in the outlet; 3. Find the total sale of the outlet; 4. Market share of a SKU is the SKU sales diveded by total sale in that outlet multiply by 100.")
    rules.append("To Calculate Imperial market share for a SKU for a product category in an outlet, follow these steps: 1. Find all the SKU fo the product category which are sold by Imperial in the outlet; 2. Then find those SKU sales in the outlet; 3. Find the total sale of the outlet; 4. Imperial Market share of a SKU is the SKU sales diveded by total sale in that outlet multiply by 100.")
    return rules

def create_vector(rules: list, new_rule_added: bool):

    VECTOR_INDEX_PATH = os.getenv("vector_index_path")
    VECTOR_INDEX_RULES = os.getenv("vector_index_rules")
    embeddings = get_embedding_model()

    if new_rule_added == False:
        print("Trying to load existing vecotr index.")
        vectordb = FAISS.load_local(folder_path=VECTOR_INDEX_PATH,embeddings=embeddings, index_name=VECTOR_INDEX_RULES, allow_dangerous_deserialization=True)

        if vectordb == None:
            print("Vector index not found. A new index will be created now.")
            if rules:
                docs = list()
                for r in rules:
                    docs.append(Document(page_content=r, metadata={"rule_no": "1" },))
                
                vectordb = FAISS.from_documents(documents=docs, embedding=embeddings)
                print(vectordb.index.ntotal)
                vectordb.save_local(folder_path=VECTOR_INDEX_PATH, index_name=VECTOR_INDEX_RULES)
            else:
                raise ValueError('The rule set is empty. Noting to put in vector database.')
    else:
        if new_rule_added == True:
            print("New Rule has been added. Creating vector again.")
            if rules:
                docs = list()
                for r in rules:
                    docs.append(Document(page_content=r, metadata={"rule_no": "1" },))
                
                vectordb = FAISS.from_documents(documents=docs, embedding=embeddings)
                print(vectordb.index.ntotal)
                vectordb.save_local(folder_path=VECTOR_INDEX_PATH, index_name=VECTOR_INDEX_RULES)
            else:
                raise ValueError('The rule set is empty. Noting to put in vector database.')
        
    return vectordb


def get_intent(query : str, vectordb : FAISS):

    if query:
        
        corpus= vectordb.similarity_search_with_relevance_scores(query=query, k=1)
        print(corpus)
        return corpus
    else:
        print("I did not receive any query to analyze")


def create_panda_smartdatalake (dataframes: list[pd.DataFrame]):

    azure_llm = get_gpt4_model()
    sdl = SmartDatalake(dataframes, config={"llm" : azure_llm, "verbose": True, "enable_cache": False}, )

    return sdl



def get_gpt35turbo_model():
        
        azure_llm = AzureOpenAI(
        model="gpt-35-turbo",
        deployment_name="IB-gpt35turbo-model",
        api_key=os.getenv('azure_openai_api_key'),
        azure_endpoint=os.getenv('azure_api_endpoint'),
        api_version="2023-07-01-preview",
        temperature=0,
        #max_tokens=4096,
        )
        return azure_llm

def get_gpt4_model():

    azure_llm = AzureChatOpenAI(
    model="gpt-4",
    deployment_name="ib-chatgpt4-model",
    api_key=os.getenv('azure_openai_api_key'),
    #api_key=os.getenv('azure_openai_api_key'),
    azure_endpoint=os.getenv('azure_api_endpoint'),
    api_version="2024-02-01", 
    temperature=0.0,)
    return azure_llm

def get_embedding_model():
    azure_embed_model = AzureOpenAIEmbeddings(
    model=os.getenv('azure_embedding_model'),
    azure_deployment="text-embedding-ada-002",
    api_key=os.getenv('azure_openai_api_key'),
    azure_endpoint=os.getenv('azure_api_endpoint'),
    #api_version="2023-08-01-preview"
    )
    return azure_embed_model

def get_gpt4_turbo_model():
    azure_llm = AzureChatOpenAI(
    model="gpt-4",
    deployment_name="ib-gpt4-turbo",
    api_key="cd76d3802fd642e7895a27ef100daf64",
    azure_endpoint="https://imperial-open-ai-eu.openai.azure.com/",
    api_version="2024-02-15-preview", 
    temperature=0.0,)
    return azure_llm

def get_simple_ib_prompt():

    prompt_template = """Brief information regarding Imperial:
    Imperial manufactures and sales tobacco products in different outlets across Germany. \
    Sales Force persons are assigned the responsibility of visiting various outlets and collect information regarding sales of Imperial products and manage the distribution. \
    
    Your Task:
    You are a sales data analyst for Imperial. Your task is to calculate different statistics based on the question asked.\
    To answer the question, you will look into the dataset and the tips provided to perform the necessary calculation.
    
    Tips:
    1. Note that the list of Imperial products can be found in product_data_en table. The table contains product data for Imperial and other manufacturer groups. \
    2. When specifically asked to calculate data for Imperial, consider Imperial sale data. If not specified, consider sales data for all manufacturers.\
    3. When calculating aggregation, always remember to remove duplicate records after merging data frames. \
    4. Sometime, Product name is also referred as SKU. """


    return prompt_template