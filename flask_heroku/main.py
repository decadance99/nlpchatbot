from flask import Flask, request, abort
import requests, json
from copy import deepcopy
app = Flask(__name__)

# LineBot Library call =====================================
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import ( MessageEvent, ButtonsTemplate, TemplateSendMessage,
    TextMessage, TextSendMessage, MessageAction,QuickReply, QuickReplyButton,
    CarouselTemplate, CarouselColumn, URIAction, FlexSendMessage
)


CHANNEL_ACCESS_TOKEN = '1jPP0q3lKPfoYYOM6oxucOEDtOEEH1aJhKH9JSmru1JhVsuPohCjp3/OiUroWgXmrjBNhIN8mbPk+/Vo21JxcjUhRmO2OG1bJFU9qX3WJooiT2O8dNm+bDkueBwZ+Zi4/fGcmrG8U+H67RjPCOMcWAdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '44d75c27530b25df54910c095c2ba060'
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
# ==========================================================

# Callback Setting -> less use to develop. better if not touch
@app.route("/callback", methods=['GET', 'POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try: handler.handle(body, signature)
    except InvalidSignatureError: abort(400)
    return 'OK'
# ==========================================================


# Previous Global variables & functions setting ========================

IMAGE_URL = "https://thinntalk.s3.ap-northeast-2.amazonaws.com/{}.png"
DETAILED_NAVER_MAP_URL = "https://m.map.naver.com/subway/subwayStation.nhn?stationId={}"
line_color = {
    "1호선": "#263c96",
    "2호선": "#3cb44a",
    "3호선": "#ff7300",
    "4호선": "#2c9ede",
    "5호선": "#8936e0",
    "6호선": "#b5500b",
    "7호선": "#697215",
    "8호선": "#e51e6e",
    "9호선": "#cea43a",
    "분당선": "#ffce33",
    "경강선": "#4192f3",
    "경의중앙선": "#9cd2bb",
    "인천 1호선": "#6f99d0",
    "인천 2호선": "#ffb850",
    "공항철도": "#73b6e4",
    "우이신설": "#c6c100",
    "경춘선": "#08af7b",
    "에버라인": "#77c371",
    "신분당선": "#D4003B",
    "의정부경전철": "#FDA600",
    "서해선": "#81A914",
    "김포골드라인": "#A17800",
    "default": "#B7B7B7",
    "black": "#000000"
}

def setting_json_form(res_json):

    json_form = json.load(open("./message_form/flex_form.json", 'r', encoding='utf-8'))
    if len(res_json['exchange_list']) > 0: json_form["header"]["contents"][0]["contents"][1]["text"] = res_json["start"]
    else: json_form["header"]["contents"][0]["contents"][1]["text"] = res_json["start"][0]
    json_form["header"]["contents"][1]["contents"][1]["text"] = res_json["end"]
    json_form["body"]["contents"][0]["text"] = json_form["body"]["contents"][0]["text"] + res_json["total_time"] + "분"

    flex_transfer = json.load(open("./message_form/flex_transfer.json", 'r', encoding='utf-8'))
    flex_inter_line = json.load(open("./message_form/flex_inter_line.json", 'r', encoding='utf-8'))
    cur_color = line_color['default']
    if len(res_json['exchange_list']) > 0:
        check = True  
        for transfer_name, line_name in res_json['exchange_list']:

            flex_transfer_tmp = deepcopy(flex_transfer)
            flex_inter_line_tmp = deepcopy(flex_inter_line)
            flex_transfer_tmp["contents"][2]["text"] = transfer_name
            if check: check = False 
            else: flex_transfer_tmp["contents"][2]["text"] += "  (환승역)"
            
            if line_name in line_color:
                cur_color = line_color[line_name]
                flex_transfer_tmp["contents"][1]["contents"][1]["borderColor"] = cur_color
                flex_transfer_tmp["contents"][2]["color"] = cur_color
                flex_inter_line_tmp["contents"][1]["contents"][0]["contents"][1]["backgroundColor"] = cur_color
                flex_inter_line_tmp["contents"][2]["color"] = cur_color
            json_form["body"]["contents"].append(flex_transfer_tmp)
            flex_inter_line_tmp["contents"][2]["text"] = line_name
            json_form["body"]["contents"].append(flex_inter_line_tmp)
    else:
        flex_transfer_tmp = deepcopy(flex_transfer)
        flex_transfer_tmp["contents"][2]["text"] = res_json["start"][0]
        line_name = res_json["start"][1]
        if line_name in line_color:
            cur_color = line_color[line_name]
            flex_transfer_tmp["contents"][1]["contents"][1]["borderColor"] = cur_color
            flex_transfer_tmp["contents"][2]["color"] = cur_color
            flex_inter_line["contents"][1]["contents"][0]["contents"][1]["backgroundColor"] = cur_color
            flex_inter_line["contents"][2]["color"] = cur_color
        json_form["body"]["contents"].append(flex_transfer_tmp)
        flex_inter_line["contents"][2]["text"] = line_name
        json_form["body"]["contents"].append(flex_inter_line)

    flex_end = deepcopy(flex_transfer)
    flex_end["contents"][2]["text"] = res_json["end"]
    flex_end["contents"][1]["contents"][1]["borderColor"] = cur_color
    flex_end["contents"][2]["color"] = cur_color

    json_form["body"]["contents"].append(flex_end)
    return  json_form

# ==========================================================


# Message Handler Setting ==================================
@handler.add(MessageEvent, message=TextMessage)
def handle_stage(event):

    req_json = dict()
    profile = line_bot_api.get_profile(event.source.user_id)
    req_json['message'] = event.message.text 
    req_json['user_id'] = event.source.user_id
    req_json['username'] = profile.display_name
    EC2_URL = "http://13.209.239.166/"

    response = requests.post(url=EC2_URL, json=req_json)

    
    status = response.status_code
    if status//100 == 2:
        res_json = response.json()
        print("res_json: ", res_json) 
        if 'stage' in res_json:
            stage = res_json['stage']

            if stage == 0:
                buttons_template = ButtonsTemplate(
                    title='궁금한 것을 알려주세요!', text='띵톡이가 할 수 있는 일들이에요.', 
                    actions=[
                        MessageAction(label='경로 내의 화장실 정보', text='경로 내'),
                        MessageAction(label='특정 역의 화장실 정보', text='특정역'),
                        MessageAction(label='최단 시간 경로 보기', text='최단 경로'),
                        MessageAction(label='최소 환승 경로 보기', text='최소 환승')
                    ]
                )
                line_bot_api.reply_message( 
                    event.reply_token, 
                    TemplateSendMessage(alt_text='기능 선택하기', template=buttons_template)
                )
                
            elif stage == 4:
                last_stage = res_json['last_stage']
                if last_stage == 1:
                    reply_msg = "{start}~{end}의 경로를 찾습니다. 어떤 경로로 검색할까요?".format(start=res_json['start'], end=res_json['end'])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text= reply_msg,
                            quick_reply= QuickReply(
                                items = [
                                    QuickReplyButton(
                                        action= MessageAction(label="최단 시간", text="최단 시간 방법")
                                    ),
                                    QuickReplyButton(
                                        action= MessageAction(label="최소 환승", text="최소 환승 방법")
                                    ),
                                    QuickReplyButton(
                                        action= MessageAction(label="출발역이 틀렸어!", text="출발역 틀림")
                                    ),
                                    QuickReplyButton(
                                        action= MessageAction(label="도착역이 틀렸어!", text="도착역 틀림")
                                    ),
                                    QuickReplyButton(
                                        action= MessageAction(label="역이 전부 틀렸어 T.T", text="역이 전부 틀림")
                                    )
                                ])))

                elif last_stage in [21, 22]:
                    reply_msg = "{start}~{end}의 경로를 찾습니다. 경로가 맞나요?".format(start=res_json['start'], end=res_json['end'])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text= reply_msg,
                            quick_reply= QuickReply(
                                items = [
                                    QuickReplyButton(
                                        action= MessageAction(label="응!! 똑똑한걸~?", text="다 맞음")
                                    ),
                                    QuickReplyButton(
                                        action= MessageAction(label="출발역이 틀렸어!", text="출발역 틀림")
                                    ),
                                    QuickReplyButton(
                                        action= MessageAction(label="도착역이 틀렸어!", text="도착역 틀림")
                                    ),
                                    QuickReplyButton(
                                        action= MessageAction(label="역이 전부 틀렸어 T.T", text="역이 전부 틀림")
                                    )
                                ])))

            # 경로 내(stage=1) 시나리오 종료 단계
            elif stage == 5:
                toilet_list = res_json['toilet_here']

                items_list = [
                    CarouselColumn(
                        thumbnail_image_url=IMAGE_URL.format(toilet_name),
                        title=toilet_name,
                        text=detailed,
                        actions= [ URIAction(label="자세히 보기", uri=DETAILED_NAVER_MAP_URL.format(code)) ]
                    ) for toilet_name, code, detailed in toilet_list
                ]

                carousel_template = CarouselTemplate(
                    columns=items_list, 
                    # image_aspect_ratio="rectangle", 
                    image_size="cover" # another options: "contain"
                )
                line_bot_api.reply_message(event.reply_token,
                    TemplateSendMessage(
                        alt_text='화장실이 있는 역 리스트',
                        template=carousel_template
                    )
                ) 
                fin_text_msg = """여기까지가 띵톡이 찾은 개찰구 내 화장실이에요!\n계속 해당 기능을 이용하시려면 'A역에서 B역으로 가는 길이야' 라고 다시 입력해 주시거나 이용을 원치 않으시면 종료'라고 입력해 주세요!"""
                line_bot_api.push_message(
                    event.source.user_id, [TextSendMessage(text=fin_text_msg)]
                )
            
            # 경로 찾기 final output
            elif stage == 23:
                
                json_form = setting_json_form(res_json)
                message = FlexSendMessage(alt_text="경로 출력", contents=json_form)
                line_bot_api.reply_message(
                    event.reply_token, message
                )
            elif stage in [11, 33, 34]:
                reply_msg = res_json['message']
                candidate_words = res_json['candidate_words']
                len_candidate = len(candidate_words)
            
                if len_candidate > 1:
                    len_candidate = len(candidate_words)
            
                    items_list = list() 
                    for i in range(len_candidate):
                        word = candidate_words[i]
                        items_list.append( QuickReplyButton(
                            action= MessageAction(label=word, text=word)
                        ))
                    
                    items_list.append(QuickReplyButton(action= MessageAction(label="찾는 역이름이 없어", text="없음")))
                
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text= reply_msg,
                            quick_reply= QuickReply(items = items_list)
                        )
                    )

                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text= reply_msg )
                    )

            elif stage == 3:
                reply_msg = res_json['message']
                candidate_words = res_json['candidate_words']
                len_candidate = len(candidate_words)
                
                if len_candidate > 1:
            
                    items_list = []
                    for i in range(len_candidate):
                        word = candidate_words[i]
                        items_list.append( QuickReplyButton(
                            action= MessageAction(label=word, text=word)
                        ))
                    
                    items_list.append(QuickReplyButton(action= MessageAction(label="찾는 역이름이 없어", text="없음")))
                
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text= reply_msg,
                            quick_reply= QuickReply(
                                items = items_list))
                    )

                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text= reply_msg )
                    )

            # 특정역(stage=10) 시나리오 종료 단계
            elif stage in [19]:
                reply_msg = res_json['message']
                
                reply_msg += "\n계속 다른 역을 찾고 싶으시면 'A'역과 같이 입력해 주시거나 이용을 종료하고 싶으시면 '종료'라고 적어주세요!"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= reply_msg )
                )

            else:   # case: stage == 11, ...
                reply_msg = res_json["message"]
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= reply_msg )
                )
    else:
        reply_msg = "예기치 않은 오류가 발생했습니다 : \n 띵톡을 다시 불러 실행해 주시거나 관리자에게 문의해 주세요ㅠㅠ"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= reply_msg )
        )

# Flask Main Setting -> running app ========================
if __name__ == "__main__":
    app.run()
# ==========================================================
