from pprint import pprint
from telnetlib import STATUS
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from django.shortcuts import render
from django.http import(
    HttpResponse, HttpResponseBadRequest, HttpResponseForbidden)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from matplotlib.pyplot import text
from pandas import value_counts
from line.models import (
    reserve_cancel, reserve_inform, reserve_search,
    userId_mapping_blockId)
from linebot import(
    LineBotApi,
    WebhookParser,
    WebhookHandler)
from linebot.exceptions import(
    InvalidSignatureError, LineBotApiError)
from linebot.models import(
    MessageEvent,
    TextSendMessage,
    FlexSendMessage,
    StickerSendMessage,
    TextMessage,
    PostbackEvent, FollowEvent,
    TemplateSendMessage, MessageTemplateAction, PostbackTemplateAction, ConfirmTemplate,
    QuickReply, QuickReplyButton, MessageAction, URIAction,
    ImagemapSendMessage, URIImagemapAction, MessageImagemapAction, Video, BaseSize, ImagemapArea, ExternalLink)
from .rest_reserve import(
    Status, Search_Status, Status_Type, Cancel_Status,
    email_identity,
    send_email,
    Json_Table,
    imagemap_timeMessage,
    imagemap_birthdayMessage,
    emoji_problem,
    emoji_time,
    emoji_survey_time,
    emoji_survey_birthday,
    emoji_survey_birthdayNotNow)
from .notionAPI import(
    createPage,
    getPage,
    deletePage
)

import json
import re  # str.spilt() multi value
from datetime import datetime, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models.functions import Cast
from django.db.models import TextField

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
web_hook_handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

#訂位資訊頁面 , id=userId


@csrf_exempt
@require_POST
# 接收訊息本體
def callback(request):
    try:
        # Signature
        signature = request.headers['X-Line-Signature']
        body = request.body.decode()
        web_hook_handler.handle(body, signature)
        print(body)
    except LineBotApiError as e:
        print(e.error.message)
    return HttpResponse("Success.")

# 處理linebot MessageEvent 事件
@web_hook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    try:
        userId = event.source.user_id
        # 回傳物件,get||create
        object, bool = reserve_inform.objects.get_or_create(
            reserve_userId=userId)
        objectSearch, boolSearch = reserve_search.objects.get_or_create(
            reserve_search_userId=userId)
        objectCancel, boolCancel = reserve_cancel.objects.get_or_create(
            reserve_cancel_userId=userId)

        print(object.reserve_status)
        status = object.reserve_status
        searchStatus = objectSearch.reserve_search_status
        cancelStatus = objectCancel.reserve_cancel_status

        message = event.message.text

        reserve_inform.objects.filter(reserve_userId=userId).update(
            reserve_status=Status_Type.STATUS_DEFAULT.value)
        reserve_search.objects.filter(reserve_search_userId=userId).update(
            reserve_search_status=Search_Status.STATUS_SEARCH_DEFAULT.value)
        reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
            reserve_cancel_status=Cancel_Status.STATUS_CANCEL_DEFAULT.value)
        ################################################

        if(message == "@同意條款並開始使用"):
            # 跳出新手指引
            guide(event)

        ################################################

        if(message == "@我要訂位"):
            reserve_inform.objects.filter(reserve_userId=userId).update(
                reserve_status=Status_Type.STATUS_NAME_DONE.value)
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                # 回傳貼圖
                [StickerSendMessage(6362, 11087922),
                 # 開始訂位
                 # TextSendMessage()
                 TextSendMessage(text="開始訂位~"),
                 TextSendMessage(text="請問您的姓名?")]
            )
        elif status == "訂位_姓名_完成" and message != "@我要查詢" and message != "@我要取消"and message != "@我要取消"and message != "@我要看餐廳":
            reserve_inform.objects.filter(reserve_userId=userId).update(
                reserve_name=message, reserve_status=Status_Type.STATUS_EMAIL_PROCESS.value)
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087931),
                 TextSendMessage(text="請問您的Email???")]
            )

        elif status == "訂位_信箱_處理" and message != "@我要查詢" and message != "@我要取消"and message != "@我要看餐廳":
            if email_identity(message) == True:
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_email=message, reserve_status=Status_Type.STATUS_EMAIL_DONE.value)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='預約時段',
                        contents=json.load(
                            open('line/build_json/reserve_time.json', 'r', encoding='utf-8'))
                    )
                )
            else:
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_status=Status_Type.STATUS_EMAIL_PROCESS.value)
                line_bot_api.reply_message(
                    event.reply_token,
                    [StickerSendMessage(6362, 11087939),
                     TextSendMessage(text="Email無效,請重新輸入")]
                )

        ################################################

        elif(message == "@我要取消"):
            reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                reserve_cancel_status=Cancel_Status.STATUS_CANCEL_NAME_DONE.value)
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                # 回傳貼圖
                [StickerSendMessage(6362, 11087922),
                 # 開始訂位
                 # TextSendMessage()
                 TextSendMessage(text="開始取消~"),
                 TextSendMessage(text="請問您的姓名?")]
            )
        elif(cancelStatus == "取消_姓名_完成" and message != "@是"and message != "@否"and message != "@我要看餐廳"and message != "@我要查詢"):
            reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                reserve_cancel_name=message, reserve_cancel_status=Cancel_Status.STATUS_CANCEL_EMAIL_PROCESS.value)
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087931),
                 TextSendMessage(text="請問您的Email????")]
            )
        elif cancelStatus == "取消_信箱_處理" and message != "@我要訂位" and message != "@我要查詢"and message != "@是"and message != "@否":
            if email_identity(message) == True:
                reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                    reserve_cancel_email=message, reserve_cancel_status=Cancel_Status.STATUS_CANCEL_EMAIL_DONE.value)

                reserveData = reserve_inform.objects.filter(
                    reserve_userId=userId).first()
                cancelData = reserve_cancel.objects.filter(
                    reserve_cancel_userId=userId).first()

                if(reserveData.reserve_name_confirm == cancelData.reserve_cancel_name
                   and reserveData.reserve_email_confirm == cancelData.reserve_cancel_email):
                    print("cancel success!")
                    # 帶入訂單資料
                    dateTimeNow = datetime.strptime(
                        datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
                    reserve_datetime = datetime.strptime(
                        str(reserveData.reserve_datetime)[:-6], '%Y-%m-%d %H:%M:%S')
                    # 如果沒找到資料 過期
                    if(reserve_datetime >= dateTimeNow):
                        reserveDateTime = reserveData.reserve_datetime.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        jsonTable = Json_Table()
                        jsonTable.reserveCancel(reserveData.reserve_name_confirm,
                                                reserveData.reserve_email_confirm,
                                                reserveDateTime)
                        line_bot_api.reply_message(
                            event.reply_token,
                            FlexSendMessage(
                                alt_text='取消結果',
                                contents=json.load(
                                    open('line/build_json/reserve_cancel_success.json', 'r', encoding='utf-8'))
                            )
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            [StickerSendMessage(8525, 16581298),
                             FlexSendMessage(
                                alt_text='查無您的資料!',
                                contents=json.load(
                                    open('line/build_json/reserve_cancel_fail.json', 'r', encoding='utf-8'))
                            )]
                        )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        [StickerSendMessage(8525, 16581298),
                         FlexSendMessage(
                            alt_text='查無您的資料',
                            contents=json.load(
                                open('line/build_json/reserve_cancel_fail.json', 'r', encoding='utf-8'))
                        )]
                    )
            else:
                reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                    reserve_cancel_status=Cancel_Status.STATUS_CANCEL_EMAIL_PROCESS.value)
                line_bot_api.reply_message(
                    event.reply_token,
                    [StickerSendMessage(6362, 11087939),
                     TextSendMessage(text="Email無效,請重新輸入")]
                )

        ################################################

        elif(message == "@我要查詢"):
            reserve_search.objects.filter(reserve_search_userId=userId).update(
                reserve_search_status=Search_Status.STATUS_SEARCH_NAME_DONE.value)
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                # 回傳貼圖
                [StickerSendMessage(6362, 11087922),
                 # 開始訂位
                 # TextSendMessage()
                 TextSendMessage(text="開始查詢~"),
                 TextSendMessage(text="請問您的姓名?")]
            )

        elif(searchStatus == "搜尋_姓名_完成")and message != "@我要看餐廳":
            reserve_search.objects.filter(reserve_search_userId=userId).update(
                reserve_search_name=message, reserve_search_status=Search_Status.STATUS_SEARCH_EMAIL_PROCESS.value)
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087931),
                 TextSendMessage(text="請問您的Email???")]
            )
        elif searchStatus == "搜尋_信箱_處理" and message != "@我要訂位" and message != "@我要取消" and message != "@是"and message != "@否"and message != "@我要看餐廳":
            if email_identity(message) == True:
                reserve_search.objects.filter(reserve_search_userId=userId).update(
                    reserve_search_email=message, reserve_search_status=Search_Status.STATUS_SEARCH_EMAIL_DONE.value)

                reserveData = reserve_inform.objects.filter(
                    reserve_userId=userId).first()
                searchData = reserve_search.objects.filter(
                    reserve_search_userId=userId).first()
                if(reserveData.reserve_name_confirm == searchData.reserve_search_name
                   and reserveData.reserve_email_confirm == searchData.reserve_search_email):
                    print("search success!")
                    # 帶入訂單資料
                    dateTimeNow = datetime.strptime(
                        datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
                    reserve_datetime = datetime.strptime(
                        str(reserveData.reserve_datetime)[:-6], '%Y-%m-%d %H:%M:%S')
                    # 如果沒找到資料 過期
                    if(reserve_datetime >= dateTimeNow):
                        reserveDateTime = reserveData.reserve_datetime.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        jsonTable = Json_Table()
                        jsonTable.reserveSearch(reserveData.reserve_name,
                                                reserveData.reserve_email,
                                                reserveDateTime)
                        line_bot_api.reply_message(
                            event.reply_token,
                            FlexSendMessage(
                                alt_text='查詢結果',
                                contents=json.load(
                                    open('line/build_json/reserve_search_success.json', 'r', encoding='utf-8'))
                            )
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            [StickerSendMessage(8525, 16581298),
                             FlexSendMessage(
                                alt_text='查無您的資料!',
                                contents=json.load(
                                    open('line/build_json/reserve_search_fail.json', 'r', encoding='utf-8'))
                            )]
                        )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        [StickerSendMessage(8525, 16581298),
                         FlexSendMessage(
                            alt_text='查無您的資料',
                            contents=json.load(
                                open('line/build_json/reserve_search_fail.json', 'r', encoding='utf-8'))
                        )]
                    )
            else:
                reserve_search.objects.filter(reserve_search_userId=userId).update(
                    reserve_search_status=Search_Status.STATUS_SEARCH_EMAIL_PROCESS.value)
                line_bot_api.reply_message(
                    event.reply_token,
                    [StickerSendMessage(6362, 11087939),
                     TextSendMessage(text="Email無效,請重新輸入")]
                )

        ################################################

        elif(message == "@我要看餐廳"):
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='餐廳資訊',
                    contents=json.load(
                        open('line/build_json/rest_info.json', 'r', encoding='utf-8'))
                )
            )

        ################################################

        elif(message == "@問卷調查"):
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(text="$$$$  $$$\n只要簡單回答幾個問題，我們準備專屬大禮包要送給你喔~$",
                                 emojis=emoji_problem()),
                 TextSendMessage(text="請點擊下方圖示，讓我們知道你最常用餐時段呢$",
                                 emojis=emoji_time()),
                 imagemap_timeMessage()
                 ]
            )

        ################################################

        elif(message == "@早餐"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087927),
                 FlexSendMessage(
                    alt_text='餐餐優惠-早餐',
                    contents=json.load(
                        open('line/build_json/rest_survey_breakfast.json', 'r', encoding='utf-8'))),
                 TextSendMessage(text="感謝你的回答$\n問卷快結束了!完成最後一題即可獲得超值好禮$",
                                 emojis=emoji_survey_time()),
                 imagemap_birthdayMessage()
                 ]
            )
        elif(message == "@午餐"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087927),
                 FlexSendMessage(
                    alt_text='餐餐優惠-午餐',
                    contents=json.load(
                        open('line/build_json/rest_survey_lunch.json', 'r', encoding='utf-8'))),
                 TextSendMessage(text="感謝你的回答$\n問卷快結束了!完成最後一題即可獲得超值好禮$",
                                 emojis=emoji_survey_time()),
                 imagemap_birthdayMessage()
                 ]
            )
        elif(message == "@晚餐"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087927),
                 FlexSendMessage(
                    alt_text='餐餐優惠-晚餐',
                    contents=json.load(
                        open('line/build_json/rest_survey_dinner.json', 'r', encoding='utf-8'))),
                 TextSendMessage(text="感謝你的回答$\n問卷快結束了!完成最後一題即可獲得超值好禮$",
                                 emojis=emoji_survey_time()),
                 imagemap_birthdayMessage()
                 ]
            )
        ################################################

        elif(message == "@1月" or message == "@2月"or message == "@3月"
             or message == "@4月"or message == "@5月"or message == "@6月"
             or message == "@7月"or message == "@8月"or message == "@9月"
             or message == "@10月"or message == "@11月"or message == "@12月"):
            subMessage = message[1:-1]
            print(subMessage)
            print(str(datetime.now().month))
            print(datetime.now() + relativedelta(day=31))
            endOfMonth = datetime.now() + relativedelta(day=31)
            print(str(endOfMonth)[:str(endOfMonth).index(" ")])
            subEndOfMonth = str(endOfMonth)[:str(endOfMonth).index(" ")]
            if(subMessage == str(datetime.now().month)):
                line_bot_api.reply_message(
                    event.reply_token,
                    [StickerSendMessage(6632, 11825378),
                     TextSendMessage(text="恭喜本月份壽星，生日快樂~$\n("+subMessage+"月壽星使用至"+subEndOfMonth+")\n\n完成問卷囉!歡迎你隨時來用餐~",
                                     emojis=emoji_survey_birthday()),
                     FlexSendMessage(
                        alt_text='問卷調查結束',
                        contents=json.load(
                            open('line/build_json/rest_survey_birthday.json', 'r', encoding='utf-8')),
                        # 2022/04/16 新增QuickReply
                        quick_reply=json.load(
                            open('line/build_json/quick_reply_after_survey.json', 'r', encoding='utf-8'))
                    )
                    ]
                )
            # 非本月壽星(當月推播)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    [StickerSendMessage(6632, 11825378),
                     TextSendMessage(text="感謝你的回答$\n我們會生日當月為你送上禮物$敬請期待唷$\n\n完成問券囉!歡迎你隨時來用餐~",
                                     emojis=emoji_survey_birthdayNotNow(),
                                     # 2022/04/16 新增QuickReply
                                     quick_reply=json.load(
                                         open('line/build_json/quick_reply_after_survey.json', 'r', encoding='utf-8'))
                                     )

                     ]
                )

        ################################################
        elif(message == "@是" and cancelStatus == "取消_雙重確認_處理"):
            try:
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_name=None,
                    reserve_email=None,
                    reserve_status=Status_Type.STATUS_DEFAULT.value,
                    # reserve_datetime = None, 時間不用管
                    reserve_name_confirm=None,
                    reserve_email_confirm=None)
                # reserve_datetime_confirm = None) 時間不用管
            except ObjectDoesNotExist:
                print("No track with the id")
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(8525, 16581295),
                 TextSendMessage(text="已成功取消訂位~"),
                 FlexSendMessage(
                    alt_text='已成功取消訂位!',
                    contents=json.load(
                        open('line/build_json/reserve_cancel_double_success.json', 'r', encoding='utf-8')))]
            )
        elif(message == "@否" and cancelStatus == "取消_雙重確認_處理"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(8525, 16581295),
                 TextSendMessage(text="已取消該動作~"),
                 FlexSendMessage(
                    alt_text='已取消該動作!',
                    contents=json.load(
                        open('line/build_json/reserve_cancel_double_fail.json', 'r', encoding='utf-8')))]
            )

        ################################################
        elif event.message.text == 'broadcast':
            line_bot_api.broadcast(TextSendMessage(
                text='宜昌小雞雞'), notification_disabled=False)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(8525, 16581298),
                 TextSendMessage(text="請問有什麼能為您服務的?")]
            )
    except LineBotApiError as e:
        print(str(e))

# 處理linebot PostbackEvent 事件
@web_hook_handler.add(PostbackEvent)
def handle_postback_message(event):
    try:
        current_tz = timezone.get_current_timezone()
        userId = event.source.user_id
        # 回傳物件,get||create
        object, bool = reserve_inform.objects.get_or_create(
            reserve_userId=userId)
        print(object.reserve_status)
        cancelObject, cancelBool = reserve_cancel.objects.get_or_create(
            reserve_cancel_userId=userId)

        status = object.reserve_status
        cancelStatus = cancelObject.reserve_cancel_status

        if event.postback.data == 'datetime':
            # 從Webhook取得回傳時間參數
            dateTimeParams = event.postback.params['datetime']
            dateTimeParams = dateTimeParams.replace("T", " ")
            print(dateTimeParams)
            # 將時間參數轉為DateTime物件
            dateTimeObject = datetime.strptime(
                dateTimeParams, '%Y-%m-%d %H:%M')
            print(dateTimeObject)
            # 當下時間
            dateTimeNow = datetime.strptime(
                datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
            # 只能預訂半年內
            dateTimeHalfYear = dateTimeNow + timedelta(days=180)
            # if status == "訂位_信箱_完成":
            # 預約過去時間->不能預訂
            if(dateTimeObject >= dateTimeNow):
                # 超過半年不能預訂
                if(dateTimeObject > dateTimeHalfYear):
                    # 禁止重複改時間
                    if status == "訂位_時間_完成":
                        pass
                    else:
                        reserve_inform.objects.filter(reserve_userId=userId).update(
                            reserve_status=Status_Type.STATUS_DATETIME_IDENTITY.value)
                        line_bot_api.reply_message(
                            event.reply_token,
                            [StickerSendMessage(6362, 11087939),
                             TextSendMessage(text="預約超過半年,請重新輸入")]
                        )
                else:
                    # 禁止重複改時間
                    if status == "訂位_時間_完成":
                        pass
                    else:
                        jsonTable = Json_Table()
                        dateTimeSpiltStr = re.split(
                            '-| |:', str(dateTimeObject))
                        print(dateTimeSpiltStr)
                        dateTimeStore = datetime(int(dateTimeSpiltStr[0]),
                                                 int(dateTimeSpiltStr[1]),
                                                 int(dateTimeSpiltStr[2]),
                                                 int(dateTimeSpiltStr[3]),
                                                 int(dateTimeSpiltStr[4]),
                                                 int(dateTimeSpiltStr[5]))
                        # 帶入訂單資料
                        reserve_inform.objects.filter(reserve_userId=userId).update(
                            reserve_datetime=dateTimeStore, reserve_status=Status_Type.STATUS_DATETIME_DONE.value)
                        print("store success")
                        reserveData = reserve_inform.objects.filter(
                            reserve_userId=userId).first()

                        jsonTable.reserveConfirm(reserveData.reserve_name,
                                                 reserveData.reserve_email,
                                                 str(reserveData.reserve_datetime)[:-6])

                        line_bot_api.reply_message(
                            event.reply_token,
                            FlexSendMessage(
                                alt_text='已取消該動作',
                                contents=json.load(
                                    open('line/build_json/reserve_confirm.json', 'r', encoding='utf-8'))
                            )
                        )
            else:
                # 禁止重複改時間
                if status == "訂位_時間_完成":
                    pass
                else:
                    reserve_inform.objects.filter(reserve_userId=userId).update(
                        reserve_status=Status_Type.STATUS_DATETIME_IDENTITY.value)
                    line_bot_api.reply_message(
                        event.reply_token,
                        [StickerSendMessage(6362, 11087939),
                         TextSendMessage(text="時間已過,請重新輸入")]
                    )
        if event.postback.data == 'cancelReserve':
            if status == "初始狀態":
                pass
            else:
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_status=Status_Type.STATUS_DEFAULT.value)

                '''2022.04.09 add 取消 要清除資料庫'''
                try:
                    reserve_inform.objects.filter(reserve_userId=userId).update(
                        reserve_name=None,
                        reserve_email=None,
                        reserve_status=Status_Type.STATUS_DEFAULT.value,
                        # reserve_datetime = None, 時間不用管
                        reserve_name_confirm=None,
                        reserve_email_confirm=None)
                    #   reserve_datetime_confirm = None) 時間不用管
                except ObjectDoesNotExist:
                    print("No track with the id")
                ''''''
                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage(text="已取消該動作~"),
                     FlexSendMessage(
                        alt_text='已取消該動作',
                        contents=json.load(
                            open('line/build_json/reserve_fail.json', 'r', encoding='utf-8'))
                    )]
                )
        if event.postback.data == 'confirmReserve':
            if status == "初始狀態":
                pass
            else:
                # 待改 單一人有多預訂 (回傳物件 多物件取first)
                reserveInformObject = reserve_inform.objects.filter(
                    reserve_userId=userId).first()

                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_name_confirm=reserveInformObject.reserve_name,
                    reserve_email_confirm=reserveInformObject.reserve_email,
                    reserve_datetime_confirm=reserveInformObject.reserve_datetime)
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_status=Status_Type.STATUS_DEFAULT.value)

                # 2022/04/16 新增userId綁定blockId
                reserveInform_confirm = reserve_inform.objects.filter(
                    reserve_userId=userId).first()
                pageDateTime = (str(reserveInform_confirm.reserve_datetime_confirm)[
                                :-6].replace(" ", "T"))

                if(userId_mapping_blockId.objects.filter(userId=userId).first() == None):
                    print("userId_mapping_blockId沒資料!")
                    # 訂單新增到Notion
                    blockId = createPage(userId,
                                        reserveInform_confirm.reserve_name_confirm,
                                        reserveInform_confirm.reserve_email_confirm,
                                        pageDateTime)
                # 判斷過期否 決定刪除資料
                else:
                    getBlockId = userId_mapping_blockId.objects.filter(
                        userId=userId).first()
                    is_expirted = getBlockId.blockId
                    print(is_expirted)
                    # 過期
                    if(getPage(is_expirted) == "True"):
                        # 訂單新增到Notion
                        blockId = createPage(userId,
                                             reserveInform_confirm.reserve_name_confirm,
                                             reserveInform_confirm.reserve_email_confirm,
                                             pageDateTime)
                    # 未過期
                    elif(getPage(is_expirted) == "False"):
                        # 先刪除紀錄再新增
                        deletePage(is_expirted)
                        blockId = createPage(userId,
                                             reserveInform_confirm.reserve_name_confirm,
                                             reserveInform_confirm.reserve_email_confirm,
                                             pageDateTime)
                    # 非預期情況
                    else:
                        print("非預期情況!")

                # userId綁定blockId model
                userId_mapping_blockId.objects.get_or_create(
                    userId=userId)
                userId_mapping_blockId.objects.filter(
                    userId=userId).update(blockId=blockId)
                ################################################

                dateTimeEmail = reserveInform_confirm.reserve_datetime_confirm.strftime(
                    "%Y-%m-%d %H:%M:%S")
                send_email(settings.EMAIL_ACCOUNT,
                           settings.EMAIL_APPLICATION_CODE,
                           reserveInform_confirm.reserve_email_confirm,
                           dateTimeEmail,
                           userId)#userId導向訂位明細

                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage(text="已成功訂位~"),
                     FlexSendMessage(
                        alt_text='已成功訂位',
                        contents=json.load(
                            open('line/build_json/reserve_success.json', 'r', encoding='utf-8'))
                    )]
                )
        if event.postback.data == 'cancel':
            if cancelStatus == "取消_雙重確認_處理":
                pass
            else:
                reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                    reserve_cancel_status=Cancel_Status.STATUS_DOUBLE_CONFIRM_PROCESS.value)
                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text='確認是否要取消',
                        template=ConfirmTemplate(
                            text='確認是否要取消',
                            actions=[
                                PostbackTemplateAction(
                                    label='是',
                                    text='@是',
                                    data='action=buy&itemid=1'
                                ),
                                MessageTemplateAction(
                                    label='否',
                                    text='@否'
                                )
                            ]
                        )
                    )
                )
    except LineBotApiError as e:
        print(str(e))

# 網頁訂位資訊頁面


def reserve_web_show(request, id):
    try:
        reserveInforms = reserve_inform.objects.get(reserve_userId=id)

        # 判斷用戶資料填寫完整否
        if reserveInforms.reserve_name_confirm == None or reserveInforms.reserve_email_confirm == None or reserveInforms.reserve_datetime_confirm == None:
            print("something is missing!")
            return render(request, "line/404.html")

        dateTime = reserveInforms.reserve_datetime_confirm
        dateTimeFormat = dateTime.strftime('%Y-%m-%d %H:%M')

        # 時間過期不顯示
        if(dateTime < timezone.now()):
            print("Expired!")
            return render(request, "line/404.html")

        year = dateTimeFormat[:4]
        month = dateTimeFormat[5:7]
        day = dateTimeFormat[8:10]
        time = dateTimeFormat[11:]

        weekDay = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        context = {
            'reserveInforms': reserveInforms,
            'year': year,
            'month': month,
            'day': day,
            'time': time,
            'weekDay': weekDay[dateTime.weekday()]
        }
        return render(request, "line/reserve.html", context)
    # 找不到用戶資訊
    except reserve_inform.DoesNotExist:
        print("DoesNotExist")
        return render(request, "line/404.html")

# 處理linebot FollowEvent 事件
@web_hook_handler.add(FollowEvent)
def handle_follow_message(event):
    jsonTable = Json_Table()
    #拿到用戶名字資料顯示在條款上
    userId = event.source.user_id
    try:
        profile = line_bot_api.get_profile(userId)
        print(profile)
        print(profile.display_name)
        jsonTable.followRole(profile.display_name)
    except LineBotApiError as e:
        print("get user information failed!")
    
    # 用戶新加入bot,推送同意條款資訊,和新手指引相關
    line_bot_api.reply_message(
        event.reply_token,
        [FlexSendMessage(
            alt_text='使用授權',
            contents=json.load(
                open('line/build_json/follow_rule.json', 'r', encoding='utf-8'))
        )]
    )


def handle_similar_message(event):
    pass

# 新手指引:基礎功能
def guide(event):
    line_bot_api.reply_message(  
        event.reply_token,
        [FlexSendMessage(
            alt_text='系統指引',
            contents=json.load(
                open('line/build_json/guide.json', 'r', encoding='utf-8'))
        )]
    )
