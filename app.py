from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)
import requests
import openai
import os
from dotenv import load_dotenv   

load_dotenv()

class Config:
    line_secret = os.getenv("line_secret")
    line_access_token = os.getenv("line_access_token")
    open_ai_key = os.getenv("open_ai_key")

app = Flask(__name__)


line_bot_api = LineBotApi(Config.line_secret)
handler = WebhookHandler(Config.line_access_token)
openai.api_key = Config.open_ai_key

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    
    if text == 'profile':
        # print ( event.source.user_id )
        # profile = line_bot_api.get_profile(event.source.user_id)
        # print(profile)
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            status = "No Status" if profile.status_message is None else profile.status_message
            
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='Display name: ' + profile.display_name
                    ),
                    TextSendMessage(
                        text='Status message: ' + status
                    )
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="Bot can't use profile API without user ID"))
    else:
        # Set the prompt for GPT to generate text based on
        prompt = text

        # Use the OpenAI API to generate text
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        # Get the generated text
        generated_text = completion.choices[0].text
        print(completion)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=generated_text.strip()))


if __name__ == "__main__":
    # app.run(host='localhost', port="5005",debug=True)
    app.run()