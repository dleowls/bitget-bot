import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 불러오기

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

import requests
import time
import base64

def place_bitget_order(symbol="BTCUSDT", side="open_long", size=0.01):
    url = "https://api.bitget.com/api/mix/v1/order/placeOrder"
    timestamp = str(int(time.time() * 1000))

    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "size": str(size),
        "side": "open_long",  # open_long: 롱 진입, close_short: 숏 종료
        "orderType": "market",
        "tradeSide": "buy",
        "productType": "umcbl",  # USDT 무기한: umcbl, 코인 무기한: dmcbl
        "clientOid": str(int(time.time()))
    }

    import json
    body_str = json.dumps(body)

    # 시그니처 생성
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


from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/hook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    if data.get("signal") == "LONG ENTRY":
        print("✅ 롱 포지션 진입 요청 들어옴!")
        place_bitget_order()  # 위에 정의된 함수 호출

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

