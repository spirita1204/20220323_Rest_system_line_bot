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

#?????????????????? , id=userId


@csrf_exempt
@require_POST
# ??????????????????
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

# ??????linebot MessageEvent ??????
@web_hook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    try:
        userId = event.source.user_id
        # ????????????,get||create
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

        if(message == "@???????????????????????????"):
            # ??????????????????
            guide(event)

        ################################################

        if(message == "@????????????"):
            reserve_inform.objects.filter(reserve_userId=userId).update(
                reserve_status=Status_Type.STATUS_NAME_DONE.value)
            line_bot_api.reply_message(  # ???????????????????????????
                event.reply_token,
                # ????????????
                [StickerSendMessage(6362, 11087922),
                 # ????????????
                 # TextSendMessage()
                 TextSendMessage(text="????????????~"),
                 TextSendMessage(text="???????????????????")]
            )
        elif status == "??????_??????_??????" and message != "@????????????" and message != "@????????????"and message != "@????????????"and message != "@???????????????":
            reserve_inform.objects.filter(reserve_userId=userId).update(
                reserve_name=message, reserve_status=Status_Type.STATUS_EMAIL_PROCESS.value)
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087931),
                 TextSendMessage(text="????????????Email???")]
            )

        elif status == "??????_??????_??????" and message != "@????????????" and message != "@????????????"and message != "@???????????????":
            if email_identity(message) == True:
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_email=message, reserve_status=Status_Type.STATUS_EMAIL_DONE.value)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text='????????????',
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
                     TextSendMessage(text="Email??????,???????????????")]
                )

        ################################################

        elif(message == "@????????????"):
            reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                reserve_cancel_status=Cancel_Status.STATUS_CANCEL_NAME_DONE.value)
            line_bot_api.reply_message(  # ???????????????????????????
                event.reply_token,
                # ????????????
                [StickerSendMessage(6362, 11087922),
                 # ????????????
                 # TextSendMessage()
                 TextSendMessage(text="????????????~"),
                 TextSendMessage(text="???????????????????")]
            )
        elif(cancelStatus == "??????_??????_??????" and message != "@???"and message != "@???"and message != "@???????????????"and message != "@????????????"):
            reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                reserve_cancel_name=message, reserve_cancel_status=Cancel_Status.STATUS_CANCEL_EMAIL_PROCESS.value)
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087931),
                 TextSendMessage(text="????????????Email????")]
            )
        elif cancelStatus == "??????_??????_??????" and message != "@????????????" and message != "@????????????"and message != "@???"and message != "@???":
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
                    # ??????????????????
                    dateTimeNow = datetime.strptime(
                        datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
                    reserve_datetime = datetime.strptime(
                        str(reserveData.reserve_datetime)[:-6], '%Y-%m-%d %H:%M:%S')
                    # ????????????????????? ??????
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
                                alt_text='????????????',
                                contents=json.load(
                                    open('line/build_json/reserve_cancel_success.json', 'r', encoding='utf-8')),
                                # 2022/04/16 ??????QuickReply
                                quick_reply=json.load(
                                    open('line/build_json/quick_reply_after_cancel.json', 'r', encoding='utf-8'))
                            )
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            [StickerSendMessage(8525, 16581298),
                             FlexSendMessage(
                                alt_text='??????????????????!',
                                contents=json.load(
                                    open('line/build_json/reserve_cancel_fail.json', 'r', encoding='utf-8'))
                            )]
                        )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        [StickerSendMessage(8525, 16581298),
                         FlexSendMessage(
                            alt_text='??????????????????',
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
                     TextSendMessage(text="Email??????,???????????????")]
                )

        ################################################

        elif(message == "@????????????"):
            reserve_search.objects.filter(reserve_search_userId=userId).update(
                reserve_search_status=Search_Status.STATUS_SEARCH_NAME_DONE.value)
            line_bot_api.reply_message(  # ???????????????????????????
                event.reply_token,
                # ????????????
                [StickerSendMessage(6362, 11087922),
                 # ????????????
                 # TextSendMessage()
                 TextSendMessage(text="????????????~"),
                 TextSendMessage(text="???????????????????")]
            )

        elif(searchStatus == "??????_??????_??????")and message != "@???????????????":
            reserve_search.objects.filter(reserve_search_userId=userId).update(
                reserve_search_name=message, reserve_search_status=Search_Status.STATUS_SEARCH_EMAIL_PROCESS.value)
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087931),
                 TextSendMessage(text="????????????Email???")]
            )
        elif searchStatus == "??????_??????_??????" and message != "@????????????" and message != "@????????????" and message != "@???"and message != "@???"and message != "@???????????????":
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
                    # ??????????????????
                    dateTimeNow = datetime.strptime(
                        datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
                    reserve_datetime = datetime.strptime(
                        str(reserveData.reserve_datetime)[:-6], '%Y-%m-%d %H:%M:%S')
                    # ????????????????????? ??????
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
                                alt_text='????????????',
                                contents=json.load(
                                    open('line/build_json/reserve_search_success.json', 'r', encoding='utf-8')),
                                # 2022/04/16 ??????QuickReply
                                quick_reply=json.load(
                                    open('line/build_json/quick_reply_after_search.json', 'r', encoding='utf-8'))
                            )
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            [StickerSendMessage(8525, 16581298),
                             FlexSendMessage(
                                alt_text='??????????????????!',
                                contents=json.load(
                                    open('line/build_json/reserve_search_fail.json', 'r', encoding='utf-8'))
                            )]
                        )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        [StickerSendMessage(8525, 16581298),
                         FlexSendMessage(
                            alt_text='??????????????????',
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
                     TextSendMessage(text="Email??????,???????????????")]
                )

        ################################################

        elif(message == "@???????????????"):
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text='????????????',
                    contents=json.load(
                        open('line/build_json/rest_info.json', 'r', encoding='utf-8'))
                )
            )

        ################################################

        elif(message == "@????????????"):
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(text="$$$$  $$$\n???????????????????????????????????????????????????????????????????????????~$",
                                 emojis=emoji_problem()),
                 TextSendMessage(text="???????????????????????????????????????????????????????????????$",
                                 emojis=emoji_time()),
                 imagemap_timeMessage()
                 ]
            )

        ################################################

        elif(message == "@??????"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087927),
                 FlexSendMessage(
                    alt_text='????????????-??????',
                    contents=json.load(
                        open('line/build_json/rest_survey_breakfast.json', 'r', encoding='utf-8'))),
                 TextSendMessage(text="??????????????????$\n??????????????????!??????????????????????????????????????????$",
                                 emojis=emoji_survey_time()),
                 imagemap_birthdayMessage()
                 ]
            )
        elif(message == "@??????"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087927),
                 FlexSendMessage(
                    alt_text='????????????-??????',
                    contents=json.load(
                        open('line/build_json/rest_survey_lunch.json', 'r', encoding='utf-8'))),
                 TextSendMessage(text="??????????????????$\n??????????????????!??????????????????????????????????????????$",
                                 emojis=emoji_survey_time()),
                 imagemap_birthdayMessage()
                 ]
            )
        elif(message == "@??????"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(6362, 11087927),
                 FlexSendMessage(
                    alt_text='????????????-??????',
                    contents=json.load(
                        open('line/build_json/rest_survey_dinner.json', 'r', encoding='utf-8'))),
                 TextSendMessage(text="??????????????????$\n??????????????????!??????????????????????????????????????????$",
                                 emojis=emoji_survey_time()),
                 imagemap_birthdayMessage()
                 ]
            )
        ################################################

        elif(message == "@1???" or message == "@2???"or message == "@3???"
             or message == "@4???"or message == "@5???"or message == "@6???"
             or message == "@7???"or message == "@8???"or message == "@9???"
             or message == "@10???"or message == "@11???"or message == "@12???"):
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
                     TextSendMessage(text="????????????????????????????????????~$\n("+subMessage+"??????????????????"+subEndOfMonth+")\n\n???????????????!????????????????????????~",
                                     emojis=emoji_survey_birthday()),
                     FlexSendMessage(
                        alt_text='??????????????????',
                        contents=json.load(
                            open('line/build_json/rest_survey_birthday.json', 'r', encoding='utf-8')),
                        # 2022/04/16 ??????QuickReply
                        quick_reply=json.load(
                            open('line/build_json/quick_reply_after_survey.json', 'r', encoding='utf-8'))
                    )
                    ]
                )
            # ???????????????(????????????)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    [StickerSendMessage(6632, 11825378),
                     TextSendMessage(text="??????????????????$\n???????????????????????????????????????$???????????????$\n\n???????????????!????????????????????????~",
                                     emojis=emoji_survey_birthdayNotNow(),
                                     # 2022/04/16 ??????QuickReply
                                     quick_reply=json.load(
                                         open('line/build_json/quick_reply_after_survey.json', 'r', encoding='utf-8'))
                                     )

                     ]
                )

        ################################################
        elif(message == "@???" and cancelStatus == "??????_????????????_??????"):
            try:
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_name=None,
                    reserve_email=None,
                    reserve_status=Status_Type.STATUS_DEFAULT.value,
                    # reserve_datetime = None, ???????????????
                    reserve_name_confirm=None,
                    reserve_email_confirm=None)
                # reserve_datetime_confirm = None) ???????????????
            except ObjectDoesNotExist:
                print("No track with the id")
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(8525, 16581295),
                 TextSendMessage(text="?????????????????????~"),
                 FlexSendMessage(
                    alt_text='?????????????????????!',
                    contents=json.load(
                        open('line/build_json/reserve_cancel_double_success.json', 'r', encoding='utf-8')))]
            )
        elif(message == "@???" and cancelStatus == "??????_????????????_??????"):
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(8525, 16581295),
                 TextSendMessage(text="??????????????????~"),
                 FlexSendMessage(
                    alt_text='??????????????????!',
                    contents=json.load(
                        open('line/build_json/reserve_cancel_double_fail.json', 'r', encoding='utf-8')))]
            )

        ################################################
        elif event.message.text == 'broadcast':
            line_bot_api.broadcast(TextSendMessage(
                text='???????????????'), notification_disabled=False)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                [StickerSendMessage(8525, 16581298),
                 TextSendMessage(text="??????????????????????????????????")]
            )
    except LineBotApiError as e:
        print(str(e))

# ??????linebot PostbackEvent ??????
@web_hook_handler.add(PostbackEvent)
def handle_postback_message(event):
    try:
        current_tz = timezone.get_current_timezone()
        userId = event.source.user_id
        # ????????????,get||create
        object, bool = reserve_inform.objects.get_or_create(
            reserve_userId=userId)
        print(object.reserve_status)
        cancelObject, cancelBool = reserve_cancel.objects.get_or_create(
            reserve_cancel_userId=userId)

        status = object.reserve_status
        cancelStatus = cancelObject.reserve_cancel_status

        if event.postback.data == 'datetime':
            # ???Webhook????????????????????????
            dateTimeParams = event.postback.params['datetime']
            dateTimeParams = dateTimeParams.replace("T", " ")
            print(dateTimeParams)
            # ?????????????????????DateTime??????
            dateTimeObject = datetime.strptime(
                dateTimeParams, '%Y-%m-%d %H:%M')
            print(dateTimeObject)
            # ????????????
            dateTimeNow = datetime.strptime(
                datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
            # ?????????????????????
            dateTimeHalfYear = dateTimeNow + timedelta(days=180)
            # if status == "??????_??????_??????":
            # ??????????????????->????????????
            if(dateTimeObject >= dateTimeNow):
                # ????????????????????????
                if(dateTimeObject > dateTimeHalfYear):
                    # ?????????????????????
                    if status == "??????_??????_??????":
                        pass
                    else:
                        reserve_inform.objects.filter(reserve_userId=userId).update(
                            reserve_status=Status_Type.STATUS_DATETIME_IDENTITY.value)
                        line_bot_api.reply_message(
                            event.reply_token,
                            [StickerSendMessage(6362, 11087939),
                             TextSendMessage(text="??????????????????,???????????????")]
                        )
                else:
                    # ?????????????????????
                    if status == "??????_??????_??????":
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
                        # ??????????????????
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
                                alt_text='??????????????????',
                                contents=json.load(
                                    open('line/build_json/reserve_confirm.json', 'r', encoding='utf-8'))
                            )
                        )
            else:
                # ?????????????????????
                if status == "??????_??????_??????":
                    pass
                else:
                    reserve_inform.objects.filter(reserve_userId=userId).update(
                        reserve_status=Status_Type.STATUS_DATETIME_IDENTITY.value)
                    line_bot_api.reply_message(
                        event.reply_token,
                        [StickerSendMessage(6362, 11087939),
                         TextSendMessage(text="????????????,???????????????")]
                    )
        if event.postback.data == 'cancelReserve':
            if status == "????????????":
                pass
            else:
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_status=Status_Type.STATUS_DEFAULT.value)

                '''2022.04.09 add ?????? ??????????????????'''
                try:
                    reserve_inform.objects.filter(reserve_userId=userId).update(
                        reserve_name=None,
                        reserve_email=None,
                        reserve_status=Status_Type.STATUS_DEFAULT.value,
                        # reserve_datetime = None, ???????????????
                        reserve_name_confirm=None,
                        reserve_email_confirm=None)
                    #   reserve_datetime_confirm = None) ???????????????
                except ObjectDoesNotExist:
                    print("No track with the id")
                ''''''
                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage(text="??????????????????~"),
                     FlexSendMessage(
                        alt_text='??????????????????',
                        contents=json.load(
                            open('line/build_json/reserve_fail.json', 'r', encoding='utf-8'))
                    )]
                )
        if event.postback.data == 'confirmReserve':
            if status == "????????????":
                pass
            else:
                # ?????? ????????????????????? (???????????? ????????????first)
                reserveInformObject = reserve_inform.objects.filter(
                    reserve_userId=userId).first()

                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_name_confirm=reserveInformObject.reserve_name,
                    reserve_email_confirm=reserveInformObject.reserve_email,
                    reserve_datetime_confirm=reserveInformObject.reserve_datetime)
                reserve_inform.objects.filter(reserve_userId=userId).update(
                    reserve_status=Status_Type.STATUS_DEFAULT.value)

                # 2022/04/16 ??????userId??????blockId
                reserveInform_confirm = reserve_inform.objects.filter(
                    reserve_userId=userId).first()
                pageDateTime = (str(reserveInform_confirm.reserve_datetime_confirm)[
                                :-6].replace(" ", "T"))

                if(userId_mapping_blockId.objects.filter(userId=userId).first() == None):
                    print("userId_mapping_blockId?????????!")
                    # ???????????????Notion
                    blockId = createPage(userId,
                                        reserveInform_confirm.reserve_name_confirm,
                                        reserveInform_confirm.reserve_email_confirm,
                                        pageDateTime)
                # ??????????????? ??????????????????
                else:
                    getBlockId = userId_mapping_blockId.objects.filter(
                        userId=userId).first()
                    is_expirted = getBlockId.blockId
                    print(is_expirted)
                    # ??????
                    if(getPage(is_expirted) == "True"):
                        # ???????????????Notion
                        blockId = createPage(userId,
                                             reserveInform_confirm.reserve_name_confirm,
                                             reserveInform_confirm.reserve_email_confirm,
                                             pageDateTime)
                    # ?????????
                    elif(getPage(is_expirted) == "False"):
                        # ????????????????????????
                        deletePage(is_expirted)
                        blockId = createPage(userId,
                                             reserveInform_confirm.reserve_name_confirm,
                                             reserveInform_confirm.reserve_email_confirm,
                                             pageDateTime)
                    # ???????????????
                    else:
                        print("???????????????!")

                # userId??????blockId model
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
                           userId)#userId??????????????????

                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage(text="???????????????~"),
                     FlexSendMessage(
                        alt_text='???????????????',
                        contents=json.load(
                            open('line/build_json/reserve_success.json', 'r', encoding='utf-8')),
                        # 2022/04/16 ??????QuickReply
                        quick_reply=json.load(
                            open('line/build_json/quick_reply_after_reserve.json', 'r', encoding='utf-8'))
                    )]
                )
        if event.postback.data == 'cancel':
            if cancelStatus == "??????_????????????_??????":
                pass
            else:
                reserve_cancel.objects.filter(reserve_cancel_userId=userId).update(
                    reserve_cancel_status=Cancel_Status.STATUS_DOUBLE_CONFIRM_PROCESS.value)
                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text='?????????????????????',
                        template=ConfirmTemplate(
                            text='?????????????????????',
                            actions=[
                                PostbackTemplateAction(
                                    label='???',
                                    text='@???',
                                    data='action=buy&itemid=1'
                                ),
                                MessageTemplateAction(
                                    label='???',
                                    text='@???'
                                )
                            ]
                        )
                    )
                )
    except LineBotApiError as e:
        print(str(e))

# ????????????????????????


def reserve_web_show(request, id):
    try:
        reserveInforms = reserve_inform.objects.get(reserve_userId=id)

        # ?????????????????????????????????
        if reserveInforms.reserve_name_confirm == None or reserveInforms.reserve_email_confirm == None or reserveInforms.reserve_datetime_confirm == None:
            print("something is missing!")
            return render(request, "line/404.html")

        dateTime = reserveInforms.reserve_datetime_confirm
        dateTimeFormat = dateTime.strftime('%Y-%m-%d %H:%M')

        # ?????????????????????
        if(dateTime < timezone.now()):
            print("Expired!")
            return render(request, "line/404.html")

        year = dateTimeFormat[:4]
        month = dateTimeFormat[5:7]
        day = dateTimeFormat[8:10]
        time = dateTimeFormat[11:]

        weekDay = ['?????????', '?????????', '?????????', '?????????', '?????????', '?????????', '?????????']
        context = {
            'reserveInforms': reserveInforms,
            'year': year,
            'month': month,
            'day': day,
            'time': time,
            'weekDay': weekDay[dateTime.weekday()]
        }
        return render(request, "line/reserve.html", context)
    # ?????????????????????
    except reserve_inform.DoesNotExist:
        print("DoesNotExist")
        return render(request, "line/404.html")

# ??????linebot FollowEvent ??????
@web_hook_handler.add(FollowEvent)
def handle_follow_message(event):
    jsonTable = Json_Table()
    #??????????????????????????????????????????
    userId = event.source.user_id
    try:
        profile = line_bot_api.get_profile(userId)
        print(profile)
        print(profile.display_name)
        jsonTable.followRole(profile.display_name)
    except LineBotApiError as e:
        print("get user information failed!")
    
    # ???????????????bot,????????????????????????,?????????????????????
    line_bot_api.reply_message(
        event.reply_token,
        [FlexSendMessage(
            alt_text='????????????',
            contents=json.load(
                open('line/build_json/follow_rule.json', 'r', encoding='utf-8'))
        )]
    )


def handle_similar_message(event):
    pass

# ????????????:????????????
def guide(event):
    line_bot_api.reply_message(  
        event.reply_token,
        [FlexSendMessage(
            alt_text='????????????',
            contents=json.load(
                open('line/build_json/guide.json', 'r', encoding='utf-8'))
        )]
    )
