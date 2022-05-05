"""
Notion Tool below:
https://developers.notion.com/
"""

from wsgiref import headers
import requests
import json
import datetime

token = "secret_vsom7MNV679gqkFaR54ds4AuOSvonQhgtGvz4JHV32a"

databaseId = "72c5a120e1764a9d9be021d77349f723"

headers = {
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer "+token
}

#新增訂單
def createPage(userId,name,email,dateTime,databaseId = databaseId, headers = headers):
    # DateTime :  ISO 8601 format date
    createUrl = "https://api.notion.com/v1/pages"

    PageData = {
        "parent": {
            "database_id": databaseId
        },
        "icon": {
            "type": "emoji",
            "emoji": "🎉"
        },
        "cover": {
            "type": "external",
            "external": {
                "url": "https://www.wanlitone.com/new/medias/article/medium/6/.png"
            }
        },
        "properties": {
            "UserId": {
                "title": [
                    {
                        "text": {
                            "content": userId
                        }
                    }
                ]
            },
            "Reserve Name": {
                "rich_text": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "Reserve Email": {
                "email": email
            },
            "Reserve DateTime": {
                "date": {
                    "start": dateTime + ".000-00:00"
                }

            }
        }
    }
    try :
        res = requests.request("POST", createUrl, headers=headers, json=PageData)
        data = res.json()
        print(res.text)
        print(res.status_code)
        print(data["id"])
        print("Notion data create successed!")
        return data["id"]

    except Exception as e :
        print("Notion data create failed!")
        return "400_errorMessage"

# 取消訂單
def deletePage(blockId):
    deleteUrl = f"https://api.notion.com/v1/blocks/{blockId}"

    try :
        res = requests.request("DELETE", deleteUrl, headers=headers)

        print(res.text)
        print(res.status_code)
        return "200_successMessage"
    except Exception as e :
        print("Notion data delete failed!")
        return "400_errorMessage"

def getPage(pageId):
    getUrl = f"https://api.notion.com/v1/pages/{pageId}"

    try :
        res = requests.request("GET",getUrl,headers=headers)

        data = res.json()
        #print(data["properties"]["Reserve DateTime"]["date"]["start"][:-10])
        #print(res.text)
        #print(res.status_code)

        compareDateTime = datetime.datetime.strptime(data["properties"]["Reserve DateTime"]["date"]["start"][:-10], '%Y-%m-%dT%H:%M:%S')
        #過期 資料不用刪除
        if(compareDateTime<datetime.datetime.now()):
            print("true")
            return "True"
        #未過期 資料刪除 避免錯誤訂單資訊
        else :
            print("false")
            return "False"
            
    except Exception as e :
        print("Notion data get failed!")
        return "400_errorMessage"

'''Test Method'''
#deletePage("8c03de28-b91e-48bf-a16c-f25204c86356")
#danie222 = createPage("kkkk2223","daniel","daniel23232344@gmail.com","2021-05-11T11:00:00")
#getPage("e0a07e63a8014fbfa2cf5a0d4d130f4d")