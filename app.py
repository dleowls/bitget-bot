import os
import time
import base64
import hmac
import hashlib
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# 🔐 환경변수 로드
load_dotenv()
API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

app = Flask(__name__)

def place_bitget_order(symbol="BTCUSDT", side="open_long", size=0.001):
    print("📦 [DEBUG] Bitget 주문 함수 진입!")  # 디버그 확인용
    print(f"📦 [DEBUG] 주문 파라미터: symbol={symbol}, side={side}, size={size}")

    url = "https://api.bitget.com/api/mix/v1/order/placeOrder"
    timestamp = str(int(time.time() * 1000))

    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "size": str(size),
        "side": side,
        "orderType": "market",
        "tradeSide": "buy",
        "productType": "umcbl",  # USDT 무기한
        "clientOid": str(int(time.time()))
    }

    body_str = json.dumps(body)
    sign_string = timestamp + "POST" + "/api/mix/v1/order/placeOrder" + body_str
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), sign_string.encode(), hashlib.sha256).digest()
    ).decode()

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=body_str)
    print(f"🔄 Bitget 응답: {response.status_code}")
    print(response.json())

@app.route("/hook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📩 받은 웹훅 데이터:", data)

        if not data:
            return jsonify({"error": "No data"}), 400

        if data.get("signal") == "LONG ENTRY":
            print("✅ 롱 포지션 진입 요청 들어옴!")
            place_bitget_order()

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print("❌ 웹훅 처리 중 에러 발생:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
