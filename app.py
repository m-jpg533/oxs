from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import webbrowser
import threading

app = Flask(__name__)

# 初始化資料庫
def init_db():
    conn = sqlite3.connect('location.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return "Flask 正常運作中"

@app.route('/logs')
def logs():
    conn = sqlite3.connect('location.db')
    c = conn.cursor()
    c.execute('SELECT latitude, longitude, timestamp FROM locations ORDER BY id DESC')
    data = c.fetchall()
    conn.close()

    def is_valid(lat, lon):
        return -90 <= lat <= 90 and -180 <= lon <= 180

    records = []
    for lat, lon, ts in data:
        records.append({
            'latitude': lat,
            'longitude': lon,
            'timestamp': ts,
            'valid': is_valid(lat, lon)
        })

    return render_template('logs.html', records=records)

@app.route('/save-location', methods=['POST'])
def save_location():
    data = request.json
    print("✅ 收到資料：", data)
    latitude = data['latitude']
    longitude = data['longitude']
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect('location.db')
    c = conn.cursor()
    c.execute('INSERT INTO locations (latitude, longitude, timestamp) VALUES (?, ?, ?)',
              (latitude, longitude, timestamp))
    conn.commit()
    conn.close()
    return {'status': 'success'}

# 只開啟一次瀏覽器
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == '__main__':
    init_db()
    threading.Timer(1.5, open_browser).start()  # 延遲 1.5 秒後自動打開瀏覽器
    app.run(host='0.0.0.0', port=5000, debug=True)
