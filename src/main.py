import sqlite3
import os
from typing import Union
from flask import Flask, redirect, Response, request, render_template

app = Flask(__name__)
DATABASE_PATH = 'urls.db'


def initialize_database() -> None:
    if os.path.exists(DATABASE_PATH):
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls'")
            if cursor.fetchone() is None:
                cursor.execute('CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT)')
    
    else:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT);')


def get_url(id: int) -> Union[str, None]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT url FROM urls WHERE id = ?', (id,))
        data = cursor.fetchone()
        if data:
            return data[0]
        return None


def store_url(url: str) -> int:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO urls (url) VALUES (?)', (url,))
        return cursor.lastrowid


def exists_url(url: str) -> bool:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT url FROM urls WHERE url = ?', (url,))
        return cursor.fetchone() is not None


def get_url_id(url: str) -> int:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM urls WHERE url = ?', (url,))
        return cursor.fetchone()[0]


def shorten_url(url: str) -> str:
    if exists_url(url):
        id = get_url_id(url)
    else:
        id = store_url(url)
    
    return request.base_url + '?id=' + str(id)
    

@app.route('/', methods=['GET'])
def index():
    id = request.args.get('id')
    if id:
        if id.isdigit():
            url = get_url(int(id))
            if url:
                return redirect(url)
        
        return Response('<h1>Invalid URL</h1>', status=404)

    url = request.args.get('url')
    if url:
        shortened_url = shorten_url(url.strip())
        return render_template('index.html', url=shortened_url)
    
    return render_template('index.html')


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)

