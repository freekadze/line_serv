const express = require('express');
const line = require('@line/bot-sdk');

// 請將以下兩個參數替換成您從 LINE Developers 平台取得的值
const config = {
  channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN || 'YOUR_CHANNEL_ACCESS_TOKEN',
  channelSecret: process.env.CHANNEL_SECRET || 'YOUR_CHANNEL_SECRET'
};

const client = new line.Client(config);
const app = express();

// 設定 webhook 路徑
app.post('/webhook', line.middleware(config), (req, res) => {
  Promise.all(req.body.events.map(handleEvent))
    .then((result) => res.json(result))
    .catch((err) => {
      console.error(err);
      res.status(500).end();
    });
});

// 處理收到的事件
function handleEvent(event) {
  // 若事件不是文字訊息，就略過
  if (event.type !== 'message' || event.message.type !== 'text') {
    return Promise.resolve(null);
  }

  // 定義 FlexSendMessage 內容
  const flexMessage = {
    type: 'flex',
    altText: '點擊前往網站',
    contents: {
      type: 'bubble',
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'text',
            text: '歡迎使用 Line Bot!',
            weight: 'bold',
            size: 'xl'
          }
        ]
      },
      footer: {
        type: 'box',
        layout: 'vertical',
        spacing: 'sm',
        contents: [
          {
            type: 'button',
            style: 'primary',
            action: {
              type: 'uri',
              label: '前往網站',
              uri: 'https://ledger-sqlite.onrender.com'
            }
          }
        ]
      }
    }
  };

  // 使用 replyMessage API 回覆 Flex Message
  return client.replyMessage(event.replyToken, flexMessage);
}

// 啟動伺服器
const port = process.env.PORT || 5000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
