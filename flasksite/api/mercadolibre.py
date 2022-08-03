import requests
import json
import pprint

CLIENT_SECRET = "corezPKoQgdUS2mZQWAJ3DfLdDGj26qL"
APP_ID = "5200906880853734"
ACCESS_TOKEN = "APP_USR-5200906880853734-080121-469ea48695b6b0362d4e2ee66c13b62d-534966925"
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
    print(resp.json())

def post_listing_tech(title, description, price, quantity,condition, warranty_time, brand, line, model, color, os, processor):

    #INFO NEEDED
    '''
    *BRAND: 
    *LINE
    *MODEL
    *COLOR
    *OS_NAME
    *PROCESSOR_BRAND
    '''

    category_id = find_category(title)

    body = {
    "title": title,
    "category_id": "MPE1652",
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
            "value_name": brand
        },
        {
            "id":"MODEL",
            "value_name": model
        },
        
        {
            "id":"COLOR",
            "value_name": color
        },
        {
            "id":"LINE",
            "value_name": line
        },
        {
            "id":"OS_NAME",
            "value_name": os
        },
        {
            "id":"PROCESSOR_BRAND",
            "value_name": processor
        }

    ],
    }

    response = listing_call(body)
    listing_id = response[0]['id']
    add_description(listing_id, description)

def post_listing_clothes(title, description, price, quantity,condition, warranty_time, brand, color, size):

    #INFO NEEDED
    '''
    *BRAND: 
    *LINE
    *MODEL
    *COLOR
    *OS_NAME
    *PROCESSOR_BRAND
    '''

    category_id = find_category(title)

    body = {
    "title": title,
    "category_id": "MPE6585",
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
            "value_name": brand
        },
        
        {
            "id":"COLOR",
            "value_name": color
        },

        {
            "id":"SIZE",
            "value_name": size
        },
    ]
    }

    response = listing_call(body)
    listing_id = response['id']
    add_description(listing_id, description)

def listing_call(body):

    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'}
    url = "https://api.mercadolibre.com/items"
    response = requests.request("POST", url, headers=headers, data=json.dumps(body))
    return response.json()

def add_description(product_id, description):

    body = {
    'plain_text': description
    }

    url = "https://api.mercadolibre.com/items/" + product_id + "/description"
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'}
    payload = json.dumps(body)
    response = requests.request("PUT", url, headers=headers, data=payload)

    return response.json()

def post_listing(title):

    product_category = find_category(title)

    if product_category == 'MPE1652':
        pass
        ##Get data

        #post_listing_tech(title)
    
    elif product_category == 'MPE6585':
        pass

        #Get Data

        #post_listing_clothes(title)

def delete_listing(product_id):
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json', "Accept": "application/json"}
    body_close = {
            "status": "closed"
            }

    body_delete = {
        "deleted": "true"
    }

    url = "https://api.mercadolibre.com/items/" + product_id


    response_close = requests.request("PUT", url, headers=headers, data=json.dumps(body_close))
    response_delete = requests.request("PUT", url, headers=headers, data=json.dumps(body_delete))

    print(response_close.json())
    print(response_delete.json())



#post_listing()
#add_description("MPE615787203")
#post_listing("MacBook Pro 16'", "MacBook nueva, no usada, modelo 2021", "6000", "2", "new", "6 meses")
#attributes_required("MPE1652")
#print(find_category("MacBook nueva, no usada, modelo 2021"))
#print(find_category("Zapatillas nike 2022 nuevas"))
#attributes_required("MPE6585")
#post_listing_clothes("Zapatillas Nike 2022", "Modelo nuevo, nuevo de fabrica", 600, 1, "new", "6 meses", "Nike", "blanco", "M")
#delete_listing("MPE615774296")