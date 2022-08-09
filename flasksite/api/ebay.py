import requests
from requests.auth import HTTPBasicAuth

# Migrate from ebay_rest library to manual API integration

# OAuth flow
# user consent -> auth code -> access token -> access user data
# GET request to auth_url to get user consent
# query params: client id, redirect_uri, response_type, scope
import config

AUTH_URL = "https://auth.sandbox.ebay.com/oauth2/authorize?client_id=AlbertTe-Resellin-SBX-db14cffb5-cfd1ac3b&response_type=code&redirect_uri=Albert_Terc-AlbertTe-Resell-zeijgqsp&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/buy.order.readonly https://api.ebay.com/oauth/api_scope/buy.guest.order https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.marketplace.insights.readonly https://api.ebay.com/oauth/api_scope/commerce.catalog.readonly https://api.ebay.com/oauth/api_scope/buy.shopping.cart https://api.ebay.com/oauth/api_scope/buy.offer.auction https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/commerce.identity.email.readonly https://api.ebay.com/oauth/api_scope/commerce.identity.phone.readonly https://api.ebay.com/oauth/api_scope/commerce.identity.address.readonly https://api.ebay.com/oauth/api_scope/commerce.identity.name.readonly https://api.ebay.com/oauth/api_scope/commerce.identity.status.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.item.draft https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/sell.item https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly"

TOKEN_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
INVENTORY_BASE_URL = "https://api.sandbox.ebay.com/sell/inventory/v1"
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

encoded_credentials = HTTPBasicAuth(config.EBAY_CLIENT_ID, config.EBAY_CLIENT_SECRET)


def get_auth_code():
    auth_response = requests.get(url=AUTH_URL)
    return auth_response


def get_access_token(auth_code):
    payload = {
        "grant_type": "authorization_code",
        "redirect_uri": "Albert_Terc-AlbertTe-Resell-zeijgqsp",
        "code": auth_code
    }
    token_response = requests.post(url=TOKEN_URL, headers=headers, auth=encoded_credentials, data=payload)
    return token_response.json()


def refresh_access_token(refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    token_response = requests.post(url=TOKEN_URL, headers=headers, auth=encoded_credentials, data=payload)
    return token_response.json()


def create_inventory_location(access_token, merchant_loc_key, address_line1, address_line2, city, state, zipcode, country):
    endpoint = "/location/"

    inventory_url = f"{INVENTORY_BASE_URL}{endpoint}{merchant_loc_key}"

    json_headers = {
        "Content-Language": "en-US",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "location": {
            "address": {
                "addressLine1": "string",
                "addressLine2": "string",
                "city": "string",
                "country": "CountryCodeEnum : [AD,AE,AF,AG,AI,AL,AM,AN,AO,AQ,AR,AS,AT,AU,AW,AX,AZ,BA,BB,BD,BE,BF,BG,BH,BI,BJ,BL,BM,BN,BO,BQ,BR,BS,BT,BV,BW,BY,BZ,CA,CC,CD,CF,CG,CH,CI,CK,CL,CM,CN,CO,CR,CU,CV,CW,CX,CY,CZ,DE,DJ,DK,DM,DO,DZ,EC,EE,EG,EH,ER,ES,ET,FI,FJ,FK,FM,FO,FR,GA,GB,GD,GE,GF,GG,GH,GI,GL,GM,GN,GP,GQ,GR,GS,GT,GU,GW,GY,HK,HM,HN,HR,HT,HU,ID,IE,IL,IM,IN,IO,IQ,IR,IS,IT,JE,JM,JO,JP,KE,KG,KH,KI,KM,KN,KP,KR,KW,KY,KZ,LA,LB,LC,LI,LK,LR,LS,LT,LU,LV,LY,MA,MC,MD,ME,MF,MG,MH,MK,ML,MM,MN,MO,MP,MQ,MR,MS,MT,MU,MV,MW,MX,MY,MZ,NA,NC,NE,NF,NG,NI,NL,NO,NP,NR,NU,NZ,OM,PA,PE,PF,PG,PH,PK,PL,PM,PN,PR,PS,PT,PW,PY,QA,RE,RO,RS,RU,RW,SA,SB,SC,SD,SE,SG,SH,SI,SJ,SK,SL,SM,SN,SO,SR,ST,SV,SX,SY,SZ,TC,TD,TF,TG,TH,TJ,TK,TL,TM,TN,TO,TR,TT,TV,TW,TZ,UA,UG,UM,US,UY,UZ,VA,VC,VE,VG,VI,VN,VU,WF,WS,YE,YT,ZA,ZM,ZW]",
                "county": "string",
                "postalCode": "string",
                "stateOrProvince": "string"
            },
            "geoCoordinates": {
                "latitude": "number",
                "longitude": "number"
            }
        },
        "locationAdditionalInformation": "string",
        "locationInstructions": "string",
        "locationTypes": [
            "StoreTypeEnum"
        ],
        "locationWebUrl": "string",
        "merchantLocationStatus": "StatusEnum : [DISABLED,ENABLED]",
        "name": "string",
        "operatingHours": [
            {
                "dayOfWeekEnum": "DayOfWeekEnum : [MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY,SUNDAY]",
                "intervals": [
                    {
                        "close": "string",
                        "open": "string"
                    }
                ]
            }
        ],
        "phone": "string",
        "specialHours": [
            {
                "date": "string",
                "intervals": [
                    {
                        "close": "string",
                        "open": "string"
                    }
                ]
            }
        ]
    }

    merchant_location_data = {
        "location": {
            "address": {
                "addressLine1": address_line1,
                "addressLine2": address_line2,
                "city": city,
                "stateOrProvince": state,
                "postalCode": zipcode,
                "country": country
            }
        },
        "locationInstructions": "Items ship from here.",
        "name": "Inventory Location 1",
        "merchantLocationStatus": "ENABLED",
        "locationTypes": [
            "STORE"
        ]
    }
    response = requests.post(url="https://api.sandbox.ebay.com/sell/inventory/v1/location/MYKEY2", headers=json_headers, data=merchant_location_data)
    return response.json()


def get_inventory_locations(access_token):
    endpoint = "https://api.sandbox.ebay.com/sell/inventory/v1/location"
    token_header = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url=endpoint, headers=token_header)
    return response.json()



if __name__ == '__main__':
    print(get_auth_code())
