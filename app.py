import re
import urllib.parse
from datetime import timedelta

import pytz
from flask import Flask, request
from notion.block import *
from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from notion_helpers import *

timezone = "Europe/Kiev"

app = Flask(__name__)

"""
my_url = https://www.notion.so/Test-task-figured-out-473c8b1a8e0640a9a3ed9d97d86fd6e7
old_url = https://www.notion.so/Test-task-figured-out-f75be4b1e7c6456280c1ae8c30e0e616
"""
def moveNotionTask(token, url):

    client = NotionClient(token)

    # нада будет найти путь от my_url до url коллекции...
    cv = client.get_collection_view(url)
    # print(type(cv))
    filter_params = {
        "filters": [
            {
                "filter": {"value": {"type": "exact", "value": "DONE"}, "operator": "enum_is"},
                "property": "Status",
            },
        ],
    }

    cv = cv.build_query(filter=filter_params)
    result = cv.execute()
    # print(result)

    for elm in result:
        """
        print("=== ",elm.name, " ====")
        print("Status = ", elm.Status)
        print("Periodicity : ", elm.Periodicity )
        print("Priority : ", elm.Priority)
        print("Set date : ", elm.Set_date.to_notion()[0][1][0][1]['start_date'] )
        print("Due date: ", elm.Due_date.to_notion()[0][1][0][1]['start_date'] ) # datetime.datetime.strptime(urllib.parse.unquote("{}".format(), "%m %d, %Y").date() ) # "%Y-%m-%dT%H:%M:%S.%fZ"
        print("Due date is today? ", elm.Due_date.to_notion()[0][1][0][1]['start_date'],
              type(datetime.datetime.now().date()),
              elm.Due_date.to_notion()[0][1][0][1]['start_date'] == str(datetime.datetime.now().date()))
        print("Due date is today? ",  elm.Due_date == datetime.datetime.now().date())
        """

        # в будущем что-то сделать с крокодилом
        duedate = datetime.date(*[int(i) for i in elm.Due_date.to_notion()[0][1][0][1]['start_date'].split('-')])
        setdate = datetime.date(*[int(i) for i in elm.Set_date.to_notion()[0][1][0][1]['start_date'].split('-')])
        if setdate < datetime.datetime.now().date():
            # если кто-то включит в Periodicity Select вместо Multiselect этот кусок кода разваливается
            # нужно как-то по другому, плюс научится учитывать день недели..
            for p in elm.Periodicity:
                if p in ['Daily']:
                    setdate = datetime.datetime.now().date()
                    elm.Due_date = setdate
                    elm.Set_date = setdate

                
                if p in ['1t/w', '2t/w', '3t/w']:
                    # print("-1 d")
                    # what a week means, needs to be clarified... 
                    if p == '1t/w':
                        duedate += datetime.timedelta(days=7) # 6 ?
                    if p == '2t/w':
                        duedate += datetime.timedelta(days=3) # 
                    if p == '3t/w':
                        duedate += datetime.timedelta(days=2) # 
                        
                    elm.Due_date = duedate 
                    elm.Set_date = duedate - datetime.timedelta(days=1)

                if p in ['1t/m', '2t/m', '1t/2w']:
                    # print("-1 w")
                    # what a month means, needs to be clarified... 
                    # 
                    if p == '1t/m':
                        duedate += datetime.timedelta(days=30) # 1 month ?
                    if p == '2t/m':
                        duedate += datetime.timedelta(days=15) # 
                    if p == '1t/2w':
                        duedate += datetime.timedelta(days=15) # 
                        
                    elm.Due_date = duedate
                    elm.Set_date = duedate - datetime.timedelta(days=7)

                if p in ['1t/2m', '1t/3m']:
                    # print("-2 w")
                    # ... 
                    if p == '1t/2m':
                        duedate += datetime.timedelta(days=60) # 2 month ?
                    if p == '1t/3m':
                        duedate += datetime.timedelta(days=90) # 
                        
                    elm.Due_date = duedate
                    elm.Set_date = duedate - datetime.timedelta(days=14)

        # if  elm.Due_date.to_notion()[0][1][0][1]['start_date'] == str(datetime.datetime.now().date())
        if setdate == datetime.datetime.now().date():
            elm.Status = 'TO DO'

        # print()
    # print(datetime.datetime.now().date())



@app.route('/done_to_todo', methods=['GET'])
def done_to_todo():
    token_v2 = os.environ.get("TOKEN")
    url = os.environ.get("URL")
    moveNotionTask(token_v2, url)
    return f'moved done_to_todo in  to Notion'


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

