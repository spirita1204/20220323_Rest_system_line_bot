import re
from enum import Enum
from django.conf import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from email.mime.image import MIMEImage
from pathlib import Path
from string import Template

from abc import ABC, abstractmethod  # 抽象繼承(blurprint)
import json

from matplotlib.style import context

# 狀態enum
from linebot.models import (
    ImagemapSendMessage, URIImagemapAction, MessageImagemapAction, Video, BaseSize, ImagemapArea, ExternalLink)


class Status_Type(Enum):
    STATUS_DEFAULT = "初始狀態"
    STATUS_NAME_DONE = "訂位_姓名_完成"
    STATUS_EMAIL_PROCESS = "訂位_信箱_處理"
    STATUS_EMAIL_DONE = "訂位_信箱_完成"
    STATUS_DATETIME_IDENTITY = "訂位_時間_判定"
    STATUS_DATETIME_DONE = "訂位_時間_完成"
    STATUS_CONFIRM_DONE = "訂位_確認_完成"
    STATUS_CANCEL_DONE = "訂位_取消_完成"


class Search_Status(Enum):
    STATUS_SEARCH_DEFAULT = "搜尋_初始狀態"
    STATUS_SEARCH_NAME_DONE = "搜尋_姓名_完成"
    STATUS_SEARCH_EMAIL_PROCESS = "搜尋_信箱_處理"
    STATUS_SEARCH_EMAIL_DONE = "搜尋_信箱_完成"


class Cancel_Status(Enum):
    STATUS_CANCEL_DEFAULT = "取消_初始狀態"
    STATUS_CANCEL_NAME_DONE = "取消_姓名_完成"
    STATUS_CANCEL_EMAIL_PROCESS = "取消_信箱_處理"
    STATUS_CANCEL_EMAIL_DONE = "取消_信箱_完成"
    STATUS_DOUBLE_CONFIRM_PROCESS = "取消_雙重確認_處理"
    STATUS_DOUBLE_CONFIRM_DONE = "取消_雙重確認_完成"


class Survey_Status(Enum):
    STATUS_SUEVEY_DEFAULT = "調查_初始狀態"
    STATUS_SUEVEY_TIME_DONE = "調查_時間_完成"
    STATUS_SUEVEY_BIRTHDAT = "調查_生日_完成"


# 沒用到
class Status():
    def __init__(self, status=Status_Type.STATUS_DEFAULT):
        self.status = status

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def change_status(self, status):
        pass


# 信箱格式確認
def email_identity(email):
    p = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not p.match(email):
        return False
    else:
        return True


# 寄通知信
def send_email(emailAccount, emailApplicationCode, recipient, datetime, url=""):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <body>
        您已預訂rest system $datetime 的用餐時段。訂位資訊如下:<a  href="$url">訂位明細</a>
    </body>
    </html>
    """
    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = "預訂成功通知!"  # 郵件標題
    content["from"] = settings.EMAIL_ACCOUNT  # 寄件者
    content["to"] = recipient  # 收件者
    # content.attach(MIMEText("您已預訂rest system " +
    #                        datetime + "的用餐時段。訂位資訊:"+url))  # 郵件內容
    template = Template(html)
    body = template.substitute(
        {"datetime": datetime, "url": "https://restaurant-system-bot.herokuapp.com/reserve/"+url})
    content.attach(MIMEText(body, "html", "utf-8"))
    content.attach(
        MIMEImage(Path("./media/RESTSYSTEM.png").read_bytes()))  # 郵件圖片內容
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(emailAccount, emailApplicationCode)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)

# 定義抽象類別


class Table(ABC):
    @abstractmethod
    def followRole(self):
        pass

    @abstractmethod
    def reserveConfirm(self):
        pass

    @abstractmethod
    def reserveSearch(self):
        pass

    @abstractmethod
    def reserveCancel(self):
        pass
# Json Table 資訊


class Json_Table(Table):
    def followRole(self, dispName):
        data = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://i.ibb.co/cv51jgx/base.png",
                "size": "full",
                "aspectRatio": "7:6",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": dispName+",歡迎使用Rest System!",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FFFFFF"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "開始使用本訂位系統前請先同意本服務",
                                        "size": "sm",
                                        "color": "#FFFFFF"
                                    },
                                    {
                                        "type": "text",
                                        "text": "與隱私條款",
                                        "size": "sm",
                                        "color": "#FFFFFF"
                                    },
                                    {
                                        "type": "text",
                                        "text": "查看條款>",
                                        "size": "sm",
                                        "color": "#00bcd4",
                                        "action": {
                                            "type": "uri",
                                            "label": "action",
                                            "uri": "https://liff.line.me/1657110099-9LmzVllQ"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "backgroundColor": "#282827"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "同意條款並開始使用",
                            "text": "@同意條款並開始使用"
                        },
                        "color": "#282827"
                    }
                ],
                "flex": 0,
                "backgroundColor": "#282827"
            }
        }
        # 寫入Trending_flex.json給line_bot_api.reply_message()載入
        with open('line/build_json/follow_rule.json', 'w') as f:
            # <--- should reset file position to the beginning.
            f.seek(0)
            json.dump(data, f)
            f.truncate()     # remove remaining part

    def reserveConfirm(self, name, email, dateTime):
        data = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": "https://i.ibb.co/rHLWK0j/base.png",
                "size": "full",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "RECEIPT",
                        "size": "sm",
                        "color": "#1DB446",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "您的訂位資訊如下:",
                        "weight": "bold",
                        "size": "md",
                        "color": "#aaaaaa"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "姓名 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": name,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "信箱 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": email,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "時間 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": dateTime,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "確認訂位",
                            "data": "confirmReserve"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "取消",
                            "data": "cancelReserve"
                        }
                    }
                ],
                "flex": 0
            }
        }
        # 寫入Trending_flex.json給line_bot_api.reply_message()載入
        with open('line/build_json/reserve_confirm.json', 'w') as f:
            # <--- should reset file position to the beginning.
            f.seek(0)
            json.dump(data, f)
            f.truncate()     # remove remaining part

    def reserveSearch(self, name, email, dateTime):
        searchData = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": "https://i.ibb.co/44G2QFN/image.png",
                "size": "full",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "RESULT",
                        "size": "sm",
                        "color": "#1DB446",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "您的訂位資訊如下:",
                        "weight": "bold",
                        "size": "md",
                        "color": "#aaaaaa"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "姓名 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": name,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "信箱 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": email,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "時間 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": dateTime,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            }
                        ]
                    }
                ]
            }
        }

        # 寫入Trending_flex.json給line_bot_api.reply_message()載入
        with open('line/build_json/reserve_search_success.json', 'w') as f:
            # <--- should reset file position to the beginning.
            f.seek(0)
            json.dump(searchData, f)
            f.truncate()     # remove remaining part

    def reserveCancel(self, name, email, dateTime):
        cancelData = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": "https://i.ibb.co/5jhwLTP/image.png",
                "size": "full",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "CANCEL",
                        "size": "sm",
                        "color": "#1DB446",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "您的訂位資訊如下:",
                        "weight": "bold",
                        "size": "md",
                        "color": "#aaaaaa"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "姓名 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": name,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "信箱 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": email,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "時間 :",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": dateTime,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "align": "end"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "取消訂位",
                            "data": "cancel"
                        },
                        "height": "sm",
                        "style": "link"
                    }
                ]
            }
        }
        # 寫入Trending_flex.json給line_bot_api.reply_message()載入
        with open('line/build_json/reserve_cancel_success.json', 'w') as f:
            # <--- should reset file position to the beginning.
            f.seek(0)
            json.dump(cancelData, f)
            f.truncate()     # remove remaining part


def imagemap_birthdayMessage():
    imagemap_message = ImagemapSendMessage(
        base_url='https://i.ibb.co/hHcTzdH/birthday1040-1-removebg-preview-2-1-1.jpg',
        alt_text='生日調查',
        base_size=BaseSize(height=1040, width=1040),
        actions=[
            MessageImagemapAction(
                text='@1月',
                area=ImagemapArea(
                    x=161,
                    y=345,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@2月',
                area=ImagemapArea(
                    x=356,
                    y=345,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@3月',
                area=ImagemapArea(
                    x=555,
                    y=345,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@4月',
                area=ImagemapArea(
                    x=746,
                    y=345,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@5月',
                area=ImagemapArea(
                    x=163,
                    y=543,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@6月',
                area=ImagemapArea(
                    x=356,
                    y=543,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@7月',
                area=ImagemapArea(
                    x=555,
                    y=543,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@8月',
                area=ImagemapArea(
                    x=746,
                    y=543,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@9月',
                area=ImagemapArea(
                    x=161,
                    y=736,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@10月',
                area=ImagemapArea(
                    x=356,
                    y=736,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@11月',
                area=ImagemapArea(
                    x=555,
                    y=736,
                    width=145,
                    height=165
                )
            ),
            MessageImagemapAction(
                text='@12月',
                area=ImagemapArea(
                    x=746,
                    y=736,
                    width=145,
                    height=165
                )
            ),
        ]
    )
    return imagemap_message


def imagemap_timeMessage():
    imagemap_timeMessage = ImagemapSendMessage(
        base_url='https://i.ibb.co/6sq91WV/pro-1-1.jpg',
        alt_text='問卷調查',
        base_size=BaseSize(height=1040, width=1040),
        actions=[
            MessageImagemapAction(
                text='@早餐',
                area=ImagemapArea(
                    x=85,
                    y=395,
                    width=259,
                    height=463
                )
            ),
            MessageImagemapAction(
                text='@午餐',
                area=ImagemapArea(
                    x=389,
                    y=395,
                    width=259,
                    height=463
                )
            ),
            MessageImagemapAction(
                text='@晚餐',
                area=ImagemapArea(
                    x=696,
                    y=395,
                    width=259,
                    height=463
                )
            )
        ]
    )
    return imagemap_timeMessage


def emoji_problem():
    emoji_problem = [
        # R
        {
            "index": 0,
            "productId": "5ac21a8c040ab15980c9b43f",
            "emojiId": "018"
        },
        # e
        {
            "index": 1,
            "productId": "5ac21a8c040ab15980c9b43f",
            "emojiId": "031"
        },
        # s
        {
            "index": 2,
            "productId": "5ac21a8c040ab15980c9b43f",
            "emojiId": "045"
        },
        # t
        {
            "index": 3,
            "productId": "5ac21a8c040ab15980c9b43f",
            "emojiId": "046"
        },
        # S
        {
            "index": 6,
            "productId": "5ac21a8c040ab15980c9b43f",
            "emojiId": "019"
        },
        # y
        {
            "index": 7,
            "productId": "5ac21a8c040ab15980c9b43f",
            "emojiId": "051"
        },
        # s
        {
            "index": 8,
            "productId": "5ac21a8c040ab15980c9b43f",
            "emojiId": "045"
        },
        # 熊大酷酷
        {
            "index": 36,
            "productId": "5ac1bfd5040ab15980c9b435",
            "emojiId": "091"
        }
    ]
    return emoji_problem


def emoji_time():
    emoji_time = [
        # 熊大親親
        {
            "index": 21,
            "productId": "5ac1bfd5040ab15980c9b435",
            "emojiId": "093"
        }
    ]
    return emoji_time


def emoji_survey_time():

    emoji_survey_time = [
        # 微笑
        {
            "index": 6,
            "productId": "5ac1bfd5040ab15980c9b435",
            "emojiId": "159"
        },
        # 愛心
        {
            "index": 29,
            "productId": "5ac1bfd5040ab15980c9b435",
            "emojiId": "218"
        }
    ]
    return emoji_survey_time


def emoji_survey_birthday():
    emoji_survey_birthday = [
        # 生日蛋糕
        {
            "index": 13,
            "productId": "5ac2213e040ab15980c9b447",
            "emojiId": "010"
        }
    ]
    return emoji_survey_birthday


def emoji_survey_birthdayNotNow():
    emoji_survey_birthdayNotNow = [
        # 生日蛋糕
        {
            "index": 6,
            "productId": "5ac1bfd5040ab15980c9b435",
            "emojiId": "098"
        },
        {
            "index": 21,
            "productId": "5ac2213e040ab15980c9b447",
            "emojiId": "027"
        },
        {
            "index": 27,
            "productId": "5ac1bfd5040ab15980c9b435",
            "emojiId": "229"
        }
    ]
    return emoji_survey_birthdayNotNow
