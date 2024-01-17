#read .ipynb file as json, and split it to each bracket, then call azure openai translate each bracket to Chinese, and save it to a new .ipynb file

import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv  

load_dotenv(override=True)
service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT") 
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME") 
key = os.getenv("AZURE_SEARCH_ADMIN_KEY") 
model: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL") 
credential = AzureKeyCredential(key)

from openai import AzureOpenAI

chatclient = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2023-05-15"
)


def translate(q):
        

    response = chatclient.chat.completions.create(
        model= os.getenv("AZURE_OPENAI_CHAT_DEPLOYED_MODEL"),
        messages=[
            {"role": "system", "content": "You are a translator. please translate the following query to Simplified Chinese, and ignore any  code/command. just keep them and the format in the response"},
            {"role": "user", "content": q}
        ]
    )

    # print(response.choices[0].message.content)
    return response.choices[0].message.content


def transIPYNB(ipnybfile):
   #parse the ipnybfile as json, and get each cell in cells[]
    #for each cell, get the content in source[]
    #for each content, call translate(content)
    #save the translated content to a new ipnybfile
    import json
    with open(ipnybfile,'r', encoding='utf-8') as f:
        data = json.load(f)
        for cell in data['cells']:
            #compbine all the source in one cell to a string
            #then call translate(source)
            #replace the source with the translated content
            #only translate the cell_type = 'markdown'
            if cell['cell_type'] != 'markdown':
                continue
            print(cell['source'])
            source = ''.join(cell['source'])
            print(source)
            new_source = translate(source)
            print(new_source)
            cell['source'] = [new_source]


        #save the translated content to a new ipnybfile, remove the .ipynb extension
        ipnybfile = ipnybfile[:-6]
        with open(ipnybfile + '_cn.ipynb', 'w') as outfile:
            json.dump(data, outfile)
            print('done')



#list files in notebook folder, and translate the first 3 files.
import os
from os import listdir
from os.path import isfile, join
notebookpath = './notebook'
#keep the full path of the file
onlyfiles = [f for f in listdir(notebookpath) if isfile(join(notebookpath, f))]
print(onlyfiles)
for file in onlyfiles[:3]:
    file = notebookpath + '/' + file
    print(file)
    transIPYNB(file)






   