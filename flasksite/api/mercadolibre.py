import requests
import json
import pprint

CLIENT_SECRET = "corezPKoQgdUS2mZQWAJ3DfLdDGj26qL"
APP_ID = "5200906880853734"
ACCESS_TOKEN = "APP_USR-5200906880853734-080112-78f5f659dcd6f68bb516a6040419c2c7-534966925"
SERVER_CODE = "https://github.com/lijemmu/crosslisting?code=TG-62e2f0dee9602a001375917b-534966925&state="
REFRESH_TOKEN = "TG-62e2f7508c8e400013fa8912-534966925"


def item_description(id):

    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN}
    url = "https://api.mercadolibre.com/items/" + id + "/description"
    resp = requests.get(url, headers=headers)

    print(resp.json())

def create_test_user():
    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN,
        'Content-type': 'application/json',
    }

    url = 'https://api.mercadolibre.com/users/test_user'

    data = '{\"site_id\":\"MPE\"}'
    

    resp = requests.post(url, headers=headers, data=data)
    print(resp.json())

def find_category(title):
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN}
    site_id = "MPE"
    product_info = title.replace(" ", "%20")
    url = "https://api.mercadolibre.com/sites/" + site_id + "/domain_discovery/search?q=" + product_info
    resp = requests.get(url, headers=headers).json()
    category_id = resp[0]['category_id']

    return category_id

def attributes_required(category_id):

    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN}
    url = "https://api.mercadolibre.com/categories/" + category_id + "/attributes"
    resp = requests.get(url, headers=headers)
    pprint.pprint(resp.json())

def post_listing(title, description, price, quantity,condition, warranty_time):

    #INFO NEEDED
    '''
    Título
    Descripción
    Estado
    Cantidad disponible
    Imágenes
    Categoría
    Precio
    Moneda
    Métodos de pago
    Envío
    Identificadores de productos
    SKU
    Variaciones
    Tipos de publicación
    Garantía del producto
    '''

    category_id = find_category(title)

    body = {
    "title": title,
    "category_id": category_id,
    "price":price,
    "currency_id":"PEN",
    "available_quantity":quantity,
    "buying_mode":"buy_it_now",
    "condition": condition,
    "listing_type_id":"gold_special",
    "sale_terms":[
        {
            "id":"WARRANTY_TYPE",
            "value_name":"Garantía del vendedor"
        },
        {
            "id":"WARRANTY_TIME",
            "value_name": warranty_time
        }
    ],
    "pictures":[
        {
            "source":"https://content.rolex.com//dam/2022/upright-cc/m126200-0020.png"
        },
        {
            "source":"https://content.rolex.com//dam/2022/laying-ba-with-shadow/m126200-0020.png"
        },
        {
            "source":"https://content.rolex.com//dam/2022/presentation-box-hr/m126200-0020.jpg"
        },
        {
            "source":"https://content.rolex.com//dam/2022/presentation-tray/m126200-0020.jpg"
        }
    ],

    "attributes":[
        {
            "id":"BRAND",
            "value_name":"Rolex"
        },
        {
            "id":"MODEL",
            "value_name":"6912"
        },
        {
            "id":"GENDER",
            "value_name":"Mujer"
        },
        {
            "id":"STRAP_COLOR",
            "value_name":"Plateado"
        },
        {
            "id":"BEZEL_COLOR",
            "value_name":"Plateado"
        },
        {
            "id":"BACKGROUND_COLOR",
            "value_name":"Verde"
        },
        {
            "id":"CASE_COLOR",
            "value_name":"Plateado"
        }

    ]
    }

    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'}
    url = "https://api.mercadolibre.com/items"
    response = requests.request("POST", url, headers=headers, data=json.dumps(body))
    print(response.json())
    #Updating with the description
    #print(add_description(response['id']), description)

def add_description(product_id, description):

    body = {
    'plain_text': description
    }

    url = "https://api.mercadolibre.com/items/" + product_id + "/description"
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'}
    payload = json.dumps(body)
    response = requests.request("PUT", url, headers=headers, data=payload)

    return response.json()


#post_listing()
#add_description("MPE615787203")
#post_listing("MacBook Pro 16'", "MacBook nueva, no usada, modelo 2021", "6000", "2", "new", "6 meses")
attributes_required("MPE1652")