from flask import Flask, send_file, abort, request,render_template,redirect,send_from_directory
#from gevent.pywsgi import WSGIServer
from gevent import pywsgi
import google.generativeai as genai
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot.models import FlexSendMessage
import requests
import json
from pydub import AudioSegment

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))
genai.configure(api_key=os.environ.get("api_key"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):
    global change_voice_flag,show_voice_flag
    try:
        uid = event.source.user_id
        UserSendAudio = line_bot_api.get_message_content(event.message.id)
        path = './static/audio/acc/'+uid+'.mp4'
        with open(path, 'wb') as fd:
            for chunk in UserSendAudio.iter_content():
                fd.write(chunk)
        if AudioSegment.from_file('./'+uid+'.mp4', format="mp4").duration_seconds < 300:
            userId=uid
            apiUrl = "https://api.tasko.uk/set_CAPTCHA_BY_UUID/" + uid;
            response = requests.get(apiUrl)
            s = response.text
            d = json.loads(s)
            url = "https://api.tasko.uk/upload-audio/"+uid+"/"+d["message"]
            
            with open(uid+".mp4", "rb") as file:
                files = {"file": (uid+".mp4", file, "audio/mpeg")}
                response = requests.post(url, files=files)
                #print(json.loads(response.text)["result"])
                reply = TextSendMessage(text=json.loads(response.text)["result"])
                line_bot_api.reply_message(event.reply_token, reply)
    except Exception as e:
        reply = TextSendMessage(text=str(e))
        line_bot_api.reply_message(event.reply_token, reply)
            
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    mtext=event.message.text
    message=[]
    #print('test')

    try:
        prompt = mtext
        genai.configure(api_key=os.environ.get("api_key"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content('我會輸入一段內容，內容可能是一個句子、或一個單字，請先理解內容後再將我提供的內容翻譯成繁體中文。回答內容請盡量口語化且符合語境，但仍保留意思。回答內容包含翻譯後的文本，不需要額外的文字。請翻譯以下段落資料：{'+prompt+'}')
        reply = TextSendMessage(text=response.text)
        
        line_bot_api.reply_message(event.reply_token, reply)
    except:
        reply = TextSendMessage(text=f"gemini err")
        line_bot_api.reply_message(event.reply_token, reply)
    #reply = TextSendMessage(text=str(s))
    #line_bot_api.reply_message(event.reply_token, reply)


from multiprocessing import cpu_count, Process

def run(MULTI_PROCESS):
    if MULTI_PROCESS == False:
        pywsgi.WSGIServer(('', 5000), app).serve_forever()
    else:
        mulserver =pywsgi.WSGIServer(('', 5000), app)
        mulserver.start()
 
        def server_forever():
            mulserver.start_accepting()
            mulserver._stop_event.wait()
 
        for i in range(2):
            p = Process(target=server_forever)
            p.start()

#if __name__ == "__main__":
    # 单进程 + 协程'f'
    #run(False)
    # 多进程 + 协程
    #run(True)

#server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
#server.serve_forever()
if __name__ == '__main__':
    app.run('127.0.0.1', 5000)






