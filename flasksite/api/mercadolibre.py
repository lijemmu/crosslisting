import requests
import json


CLIENT_SECRET = "corezPKoQgdUS2mZQWAJ3DfLdDGj26qL"
APP_ID = "5200906880853734"
ACCESS_TOKEN = "APP_USR-5200906880853734-072816-256471d3cdd55324d9ff6679dddc8725-53496692"
SERVER_CODE = "https://github.com/lijemmu/crosslisting?code=TG-62e2f0dee9602a001375917b-534966925&state="


def item_description(id):

    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN}
    url = "https://api.mercadolibre.com/items/" + id + "/description"
    resp = requests.get(url, headers=headers)

    print(resp.json())




print(item_description("MPE605816430"))