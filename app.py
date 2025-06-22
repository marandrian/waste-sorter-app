from flask import Flask, render_template, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Data counter
data = {
    'metal_count': 0,
    'non_metal_count': 0,
    'last_reset': datetime.now().date(),
    'pending_command': None
}

def reset_daily():
    """Reset counters daily at midnight"""
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            data['metal_count'] = 0
            data['non_metal_count'] = 0
            data['last_reset'] = now.date()
            print("Daily counters reset!")
        time.sleep(60)

# Start reset thread
reset_thread = threading.Thread(target=reset_daily)
reset_thread.daemon = True
reset_thread.start()

@app.route('/')
def dashboard():
    total = data['metal_count'] + data['non_metal_count']
    return render_template('dashboard.html', 
                           metal_count=data['metal_count'],
                           non_metal_count=data['non_metal_count'],
                           total=total,
                           last_reset=data['last_reset'])

@app.route('/update', methods=['POST'])
def update_data():
    content = request.json
    if content['type'] == 'metal':
        data['metal_count'] = content.get('metal_count', data['metal_count'])
    elif content['type'] == 'non_metal':
        data['non_metal_count'] = content.get('non_metal_count', data['non_metal_count'])
    
    response = jsonify({"status": "success"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200

@app.route('/command', methods=['GET', 'POST'])
def handle_command():
    if request.method == 'POST':
        command = request.json.get('command')
        if command in ['metal', 'non_metal', 'neutral']:
            data['pending_command'] = command
            print(f"Received command: {command}")
            
            response = jsonify({"status": "command received"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
            
        response = jsonify({"error": "invalid command"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 400
    
    elif request.method == 'GET':
        command = data['pending_command']
        data['pending_command'] = None
        
        if command:
            print(f"Sending command to ESP: {command}")
            response = jsonify({"command": command})
        else:
            response = jsonify({})
            
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

# Middleware untuk CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)