import os, sys, datetime, random, json
from flask import Flask, session, g, request, render_template, redirect, Response
from flask_mongoengine import MongoEngine

import config
from models import DownloadLog

app = Flask(__name__)

app.config.from_object('config.Config')
db = MongoEngine(app)


@app.before_request
def before_request():
    if request.headers.getlist("X-Forwarded-For"):
        g.last_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        g.last_ip = request.remote_addr


@app.route('/')
def index_view():
    return render_template('index.html')


@app.route('/downloads')
def downloads_view():
    with open('./downloads.json') as f:
        downloads = json.load(f)
        for download in downloads:
            download['download-count'] = DownloadLog.objects.filter(key=download['repo-name']).count()

            # In September 2019, our server was initialized, and we lost the download log data.
            # This line restores the previous download count by adding the previous download count as the default.
            # To prevent such data loss, we uploaded our code on SourceForge (https://sourceforge.net/u/nlpcl-forge).
            if 'default-download-count' in download:
                download['download-count'] += download['default-download-count']

        return render_template('downloads.html', downloads=downloads, DownloadLog=DownloadLog)


@app.route('/apis')
def apis_view():
    return render_template('apis.html')


@app.route('/api/download/log', methods=['POST'])
def download_log():
    data = request.get_json()
    key = data['key']

    print(".environ['REMOTE_ADDR'] :", request.environ['REMOTE_ADDR'])
    print("request.remote_addr :", request.remote_addr)

    log = DownloadLog(key=key, ip=g.last_ip)
    log.save()

    return Response('success', status=200)


if __name__ == '__main__':
    base_dir = os.path.abspath(os.path.dirname(__file__) + '/')
    sys.path.append(base_dir)

    app.secret_key = config.Config.SECRET_KEY
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', True)
    app.run(host='0.0.0.0', debug=FLASK_DEBUG, port=8080)
