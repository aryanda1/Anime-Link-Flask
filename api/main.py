from flask import Flask,request,jsonify
import json
from gogo_scrap import search,get_links,get_download_links
from flask_cors import CORS
import requests as req
from bs4 import BeautifulSoup
from uuid import uuid1
import os
import psycopg2

app = Flask(__name__)
# cors = CORS(app,resources={r'/api/*':{'origins':'https://anime-link-gen.vercel.app'}})
cors = CORS(app,resources={r'/api/*':{'origins':'*'}})
connection = psycopg2.connect(os.environ.get('DB_URL'))
create_table = ("CREATE TABLE IF NOT EXISTS data(id text primary key,gogoid Text,source Text,totaleps Text,downloadlinks Text);")

@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})

@app.route('/api/search', methods=['POST'])
def searchAnime():
    # headers = request.headers
    # auth_token = headers.get('authorization-sha256')
    # if not auth_token:
    #     return 'Unauthorized', 401
    uid = str(uuid1())
    sql = ("INSERT INTO data(id) VALUES(%s);")
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(create_table)
            cursor.execute(sql,(uid,))
    data = request.json
    an_name = data['an_name']
    an_dets = search(an_name)
    return jsonify({'results':an_dets,'uniqueId':uid})

@app.route('/api/episodesCount', methods=['POST'])
def getEpisodeCount():
    data = request.json
    name = data['name']
    uniqueId = data['id']

    source = f"https://gogoanime.pe/category/{name}"
    try:
        with req.get(source) as res:
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "html.parser")
                all_episodes = soup.find("ul", {"id": "episode_page"})
                lines = (all_episodes.get_text().split("\n"))
                for line in reversed(lines):
                    if(line!=''):
                        break

                all_episodes = int(
                    line.split("-")[-1])
            else:
                return {'status':501,'message':'Anime not found. Please try again.'}
    except Exception as e:
        return {'status':501,'error':e}
    sql = ("UPDATE data SET gogoId = %s, source = %s, TotalEps = %s WHERE id = %s;")
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (name,source,all_episodes,uniqueId))
    # data = cur.execute('''SELECT * FROM data''')
    # for row in data:
    #     print(row)
    return {'epsNo':all_episodes}


@app.route('/api/getEps',methods=['POST'])
def getlink():
    data = request.json
    ep = data['ep']
    uniqueId = data['id']
    # print(ep)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM data where id = %s;",(uniqueId,))
            row = cursor.fetchone()
    # print(row['id'])
    # print(row['downloadLinks'] == None)
    links = []
    if row[4] ==None:
        links = (get_links(row[1],int(row[3]),row[2]))
        sql = "UPDATE data SET DownloadLinks = %s WHERE id = %s;"
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql,(json.dumps(links),uniqueId))
    else:
        links = json.loads(row[4])
    return {'download':get_download_links(links[ep])}