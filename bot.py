from flask import Flask, send_file, abort, request,render_template,redirect,send_from_directory
#from gevent.pywsgi import WSGIServer
from gevent import pywsgi
import google.generativeai as genai

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot.models import FlexSendMessage


app = Flask(__name__)

url_out='https://99fe-2403-c300-c903-70a4-6bfb-22bb-b325-d314.ngrok-free.app'
trade_num=''
trade_order=''
trade_sell_hex=''
#url_out=get_ngrok_url()

canvas_color = '#fffafa'
line_color = '#c8ced1'
font_color = '#171510'
colorup = '#bf0000'
colordown = '#0d9101'


#########################################
'''
def get_ngrok_url():
    url = "http://localhost:4040/api/tunnels"
    res = requests.get(url)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    for i in range(len(res_json)):
        if(res_json["tunnels"][i]["proto"]=='https'):
            return res_json["tunnels"][i]["public_url"]
            break
            
url_out=get_ngrok_url()
'''
list_stock_user=['U2b12c5d1919feab6eaa7e9c94a50a113','Uda5dff485f350f2f4b6a7deb3c93c5a2']

postback_hex=''
check_hex=''

line_bot_api = LineBotApi('+EDyb8hkvT3qCz32f4CYSGLxJyOBvAb3ctdTHxJUWM5tMixeZH8b9TV9uXjhxs+wzcdBhHPUNc+k6D0Vf2Pv9ah5tdR864pzD3xGamfKaVgobSoLlEAqY0DqxQegNPdy/rxYNGKmDGZICLX9O+3BpwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler("ac4e044ffb47baeaeef095785f348f6c")
genai.configure(api_key='AIzaSyDYKqrTZKsa9_CixwLaSS-rsVC_FD2V--Y')
      
list_hsm_user=['U20d461d043da1a849626e06711c327f3']
list_c_user=['U20d461d043da1a849626e06711c327f3']
list_mt4_user=['U20d461d043da1a849626e06711c327f3']
list_a32_user=['U20d461d043da1a849626e06711c327f3']

def notify(request):
    pattern = 'code=.*&'

    raw_uri = request.get_raw_uri()

    codes = re.findall(pattern,raw_uri)
    for code in codes:
        code = code[5:-1]
        print(code)

    #抓取user的notify token
    user_notify_token_get_url = 'https://notify-bot.line.me/oauth/token'
    params = {
        'grant_type':'authorization_code',
        'code':code,
        'redirect_uri':'https://eb2614c8d58c.ngrok.io/notify',#這邊改成自己的https://ngrok domain/notify
        'client_id':'ibT0c6xbuGOsWlHofoKZrU',#這邊改成自己的Notify client_id
        'client_secret':'PMIBpMHjvZvaf7HZz6CsoEnAGTQYOlSIlBkICPiZVkV' #這邊改成自己的Notify client_secret

    }
    get_token = requests.post(user_notify_token_get_url,params=params)
    print(get_token.json())
    token = get_token.json()['access_token']
    print(token)

    #抓取user的info
    user_info_url = 'https://notify-api.line.me/api/status'
    headers = {'Authorization':'Bearer '+token}
    get_user_info = requests.get(user_info_url,headers=headers)
    print(get_user_info.json())
    notify_user_info = get_user_info.json()
    if notify_user_info['targetType']=='USER':
        User_Info.objects.filter(name=notify_user_info['target']).update(notify=token)
    elif notify_user_info['targetType']=='GROUP':
        pass
    return HttpResponse()

@app.route("/", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        s='''功能如下:
            傳送位置可知道該地天氣
            星座:當日星座運勢
            油價:中油油價
            asis:asis程控
            resethsm: 重開熱軋首頁
            銷售進度:銷售進度
            新聞:最新新聞'''
        return "<H2>Welcome to Line Bot !!</H2>指令如下:"+s
        #return redirect("http://bot4ko.site/static/.well-known/acme-challenge/TSjOiUk_UFOvKnHi79t9GSoIiojdCbWbg3hB8j_kr5g", code=302)
        #return "<a href='./static/.well-known/acme-challenge/TSjOiUk_UFOvKnHi79t9GSoIiojdCbWbg3hB8j_kr5g' target='_blank'>TSjOiUk_UFOvKnHi79t9GSoIiojdCbWbg3hB8j_kr5g</a>"

    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    mtext=event.message.text
    message=[]
    #print('test')

    try:
        prompt = mtext
        genai.configure(api_key="AIzaSyDYKqrTZKsa9_CixwLaSS-rsVC_FD2V--Y")
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
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


# In[ ]:




