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
my_url = https://www.notion.so/Test-task-figured-out-f75be4b1e7c6456280c1ae8c30e0e616
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
        setdate = datetime.date(*[int(i) for i in elm.Due_date.to_notion()[0][1][0][1]['start_date'].split('-')])
        setdate1 = datetime.date(*[int(i) for i in elm.Set_date.to_notion()[0][1][0][1]['start_date'].split('-')])
        if setdate1 < datetime.datetime.now().date():
            for p in elm.Periodicity:
                if p in ['Daily']:
                    elm.Due_date = datetime.datetime.now().date()
                    elm.Set_date = datetime.datetime.now().date()

                
                if p in ['1t/w', '2t/w', '3t/w']:
                    # print("-1 d")
                    dt = setdate - datetime.timedelta(days=1)
                    elm.Set_date = dt

                if p in ['1t/m', '2t/m', '1t/2w']:
                    # print("-1 w")
                    dt = setdate - datetime.timedelta(days=7)
                    elm.Set_date = dt

                if p in ['1t/2m', '1t/3m']:
                    # print("-2 w")
                    dt = setdate - datetime.timedelta(days=14)
                    elm.Set_date = dt

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

