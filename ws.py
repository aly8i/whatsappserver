from datetime import datetime
from flask import Flask,jsonify,request
import requests
import base64
import json
from flask_cors import CORS
import time


clientserver_url = "http://localhost:3001"
# whatsappserver_url = "http://localhost:3000"
whatsappserver_url = "https://alien.tail2a91d1.ts.net"



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/start')
def startSession():
    endpoint = f"/api/sessions/start"
    url = f"{whatsappserver_url}{endpoint}"
    data = {
        "name": "default",
        "config": {
            "proxy": None,
            "webhooks": [
                {
                    "url": "https://httpbin.org/post",
                    "events": [
                    "message",
                    "session.status"
                    ],
                    "hmac": None,
                    "retries": None,
                    "customHeaders": None
                }
            ]
        }
    }
    json_data = json.dumps(data)
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json_data, headers=headers)
    if response.status_code == 200 or response.status_code == 201:
        print("Request successful!")
        print("Response:", response.json())
    else:
        print(f"Request failed with status code {response.status_code}")
    print("Response content:", response.text)
    return response.json()

@app.route("/check")
def get_screenshot():
    endpoint = "/api/screenshot?session=default"
    url = whatsappserver_url + endpoint
    response = requests.get(url)
    # time.sleep(2)
    if response.status_code == 200:
        image_data = response.content
        base64_image = base64.b64encode(image_data).decode("utf-8")
        data = {"base64": base64_image}
        return jsonify(data), 200
    else:
        print(f"Request failed with status code {response.status_code}")
        print("Response content:", response.text)
    return response.json()

@app.route("/check2")
def checklogin():
    endpoint = "/api/screenshot?session=default"
    url = whatsappserver_url + endpoint
    response = requests.get(url)
    time.sleep(2)
    if response.status_code == 200:
        image_data = response.content
        base64_image = base64.b64encode(image_data).decode("utf-8")
        data = {"base64": base64_image}
        return jsonify(data), 200
    else:
        print(f"Request failed with status code {response.status_code}")
        print("Response content:", response.text)
    return response.json()

@app.route('/get', methods=['GET'])
def getChat():
    endpoint = "/api/messages"
    number = request.args.get('number')    

    if not number :
        return jsonify({'error': 'Invalid request. Please provide number.'}), 400
    
    url = f"{whatsappserver_url}{endpoint}?chatId={number}@c.us&limit=10&session=default&downloadMedia=false"
    response = requests.get(url)
    print(response.json()[0]['id'])
    if response.status_code == 200:
        print(' got messages successfully!')
        for msg in reversed(response.json()):
            lastmsg = "No Message Found"
            if "Hello" in msg['body']:
                lastmsg = msg['body']
                break
        return jsonify(lastmsg), 200
    else:
       print('Failed to get messages. Status code:', response.status_code) 
       return jsonify(response.status_code), 400
    

@app.route('/invoice/<u_name>/<u_phonenumber>/<u_previous_balance>/<u_current_payment>/<u_day>', methods=['GET'])
def sendInvoice(u_name,u_phonenumber,u_previous_balance,u_current_payment,u_day):    
    try:

        if len(u_phonenumber) == 8:
            if  u_phonenumber.startswith("03") or u_phonenumber.startswith("05") or u_phonenumber.startswith("07") or u_phonenumber.startswith("01"):
                u_phonenumber = "961" + u_phonenumber[1:]
            elif u_phonenumber.startswith("71") or u_phonenumber.startswith("70") or u_phonenumber.startswith("78") or u_phonenumber.startswith("79") or u_phonenumber.startswith("76") or u_phonenumber.startswith("80") or u_phonenumber.startswith("81"):
                u_phonenumber = "961" + u_phonenumber
        
        elif len(u_phonenumber) > 8:
            if not u_phonenumber.startswith("+"):
                u_phonenumber = "" + u_phonenumber
                print("national number")
            else:
                print("national")
        else :
            print("phonenumber error")
            return jsonify("phonenumber error") , 400
        
        if ( u_day == 0 ):
            print("date error")
            return "Date error"

        if ( u_current_payment == 0 ):
            print("balance error")
            return jsonify("balance error"),400

        current_date = datetime.now()
        current_month = current_date.month
        current_day = current_date.day
        
        if current_day < float(u_day):
            current_month -= 1
        if current_month == 12:
            next_month = 1
            next_year = current_date.year + 1
        else:
            next_month = current_month + 1
            next_year = current_date.year
        date_now = current_date.strftime("%Y-%m-%d")
        u_remaining_balance = float(u_previous_balance) - float(u_current_payment)
        u_name = u_name.encode('utf-8').decode('utf-8')
        u_name_arr = u_name.split("20%");
        u_name= " ".join(u_name_arr)
        
        message = "YGI Net وصل"+ "\n\n" + "الاسم :"+ u_name + "\n"  +"قيمة الدفع :" + "$" + str(u_current_payment) + "\n" + "الحساب الباقي :" + "$" + str(u_previous_balance)  + "\n" + "لغاية :" + str(next_year) + "-" + str(next_month) + "-" + str(u_day) + "\n\n" "التاريخ :" + date_now 
        print(message);
        endpoint = "/api/sendText"
        url = whatsappserver_url + endpoint
        data = {
            'chatId': f"{u_phonenumber}@c.us",
            'text': message,
            'session': 'default'
        }
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print('Message sent successfully!')
            return jsonify(data), 200
        else:
            print('Failed to send message. Status code:', response.status_code) 
        return jsonify(response.status_code), 400
    except():
        print("error")
    return "ok"
     


@app.route('/send', methods=['GET'])
def send_message():
    endpoint = "/api/sendText"
    url = whatsappserver_url + endpoint
    number = request.args.get('number')
    message = request.args.get('message')
    
    if not number or not message:
        return jsonify({'error': 'Invalid request. Please provide both number and message.'}), 400
    data = {
        'chatId': f"{number}@c.us",
        'text': message,
        'session': 'default'
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print('Message sent successfully!')
        return jsonify(data), 200
    else:
        print('Failed to send message. Status code:', response.status_code) 
        return jsonify(response.status_code), 400
    

@app.route("/qr")
def get_qr_code():
    
    endpoint = f"/api/default/auth/qr"
    params = {
        "format": "image",
        "session":"default"
    }

    response = requests.get(f"{whatsappserver_url}{endpoint}", params=params)
    time.sleep(2)
    if response.status_code == 200:
        image_data = response.content
        base64_image = base64.b64encode(image_data).decode("utf-8")
        print(base64_image);
        data = {"base64": base64_image}
        return jsonify(data), 200
    else:
        print(f"Request failed with status code {response.status_code}")
        print("Response content:", response.text)
    return response.json()
    
@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
