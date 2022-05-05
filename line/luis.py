import json
from msilib.schema import Error
import requests
from sqlalchemy import PrimaryKeyConstraint

# 金鑰
primaryKey = "8b3aed6e8491444b9845d77d21418845"
# 備用
secondaryKey = "14726e653b5a489d9612e596d7279569"


def luis_similar_keywod(query):
    luisUrl = ("https://eastasia.api.cognitive.microsoft.com/luis/prediction/v3.0/apps/"
               + "0ee869e6-0292-47a0-8314-c5f526770577/slots/production/predict?verbose=true&show-all-intents=true&log=true&"
               + "subscription-key="+primaryKey+"&query="+query)

    res = requests.request("GET", luisUrl)

    data = res.json()

    try:
        # 將json轉儲為dict 解析tag
        jsonDict = json.dumps(data["prediction"]["entities"])
        '''
        {
            "query":"取消",
            "prediction":{
                "topIntent":"rest_system",
                "intents":{
                    "rest_system":{
                        "score":0.9847927
                    },
                    "None":{
                        "score":0.013565115
                    }
                },
                "entities":{
                    "@我要取消":[
                        "取消"
                    ],
                    "$instance":{
                        "@我要取消":[
                            {
                            "type":"@我要取消",
                            "text":"取消",
                            "startIndex":0,
                            "length":2,
                            "score":0.94128966,
                            "modelTypeId":1,
                            "modelType":"Entity Extractor",
                            "recognitionSources":[
                                "model"
                            ]
                            }
                        ]
                    }
                }
            }
        }
        '''
        print(list(json.loads(jsonDict).keys())[0])
    except Exception :
        #未找到關鍵詞
        pass
luis_similar_keywod("取sss消")
