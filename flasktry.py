import requests
import json
from flask import Flask
from flask import request
from flask import jsonify
from flask import abort, redirect, url_for
import re
from datetime import datetime
from flasgger import Swagger
from flasgger.utils import swag_from

app = Flask(__name__)
Swagger(app)


@app.route('/', methods=['GET'])
def health():
    return redirect(url_for('apidocs'))


@app.route('/apidocs/', methods=['POST', 'GET'])
def apidocs():
    print("inside api docs")


@app.route('/search/', methods=['GET'])
@swag_from('index.yml')
def search():
    error = None
    print(request.method)
    if request.method == 'GET':
        searchword = request.args.get('searchparam', '')
        fromdate = request.args.get('from', '')
        todate = request.args.get('to', '')
        return searchElastic(searchword, fromdate, todate)


def searchElastic(word, fromdate, todate):
    if fromdate == '' and todate == '':
        fromdate = "1857-01-01"
        todate = "3000-01-01"
    validhits = []
    dateList = []
    print('http://localhost:9200/' + word + '/_search')
    try:
        result = requests.get('http://localhost:9200/' + word + '/_search?scroll=100m&size=905').content
        Response = json.loads(result.decode('utf-8'))
        # jsonResponse=jsonify(Response)
        # print(jsonResponse)
        total = Response['hits']['total']
        for i in range(0, len(Response['hits']['hits'])):
            text = Response['hits']['hits'][i]['_source']['Text']
            created_at = Response['hits']['hits'][i]['_source']['date']
            date = convertDate(created_at)
            if fromdate <= date <= todate:
                validhits.append(text)
                dateList.append(date)

        dateList.sort()
        startdate = dateList[0]
        enddate = dateList[(len(dateList)) - 1]
        return jsonify(
            search_param=word,
            total_hits=total,
            start_date=startdate,
            end_date=enddate,
            tweets=validhits
        )
    except Exception:
        return jsonify(
            search_param=word,
            total_hits=0,
            start_date="",
            end_date="",
            tweets=[]
        )

def convertDate(unformatted):
    remove_ms = lambda x: re.sub("\+\d+\s", "", x)
    mk_dt = lambda x: datetime.strptime(remove_ms(x), "%a %b %d %H:%M:%S %Y")
    my_form = lambda x: "{:%Y-%m-%d}".format(mk_dt(x))
    result = my_form(unformatted)
    return result


app.run(debug=True,host="0.0.0.0", port=80)
