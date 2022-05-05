import json
import requests
from sqlalchemy import PrimaryKeyConstraint

# 金鑰
primaryKey = "8b3aed6e8491444b9845d77d21418845"
# 備用
secondaryKey = "14726e653b5a489d9612e596d7279569"


def luis_similar_keywod(query):
    luisUrl = ("https://eastasia.api.cognitive.microsoft.com/luis/prediction/v3.0/apps/"
    +"0ee869e6-0292-47a0-8314-c5f526770577/slots/production/predict?verbose=true&show-all-intents=true&log=true&"
    +"subscription-key="+primaryKey+"&query="+query)

    res = requests.request("GET",luisUrl)

    data = res.json()

    print(data)

luis_similar_keywod("訂餐")