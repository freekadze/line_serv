const express = require('express');
const line = require('@line/bot-sdk');

// 請將以下兩個參數替換成您從 LINE Developers 平台取得的值
const config = {
  channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN || 'JVTDoyRsx/uSuO4DyyYcw8OUg6UX5pUQENypv/Y2xrys8E/LxZ71miSQlpuaA3YE/i/jPwHPisg0p869cMl8THcgzO4C2UXFFuBsLNB2BIa8QFIAEsSiNDTxt0pNudTgLKat6K2e9ci90x+LcMRzlgdB04t89/1O/w1cDnyilFU=',
  channelSecret: process.env.CHANNEL_SECRET || '8fa160b22c30173b529b88b2c49b0067'
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
            text: '歡迎使用 TasKo分帳',
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
              label: '新增記錄',
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
