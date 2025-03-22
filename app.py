from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/hook', methods=['POST'])
def webhook():
    data = request.json
    print("🚨 Webhook received:", data)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
