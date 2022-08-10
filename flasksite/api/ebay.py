import requests
from requests import JSONDecodeError
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
encoded_credentials = HTTPBasicAuth(config.EBAY_CLIENT_ID, config.EBAY_CLIENT_SECRET)


class EbayAPI:

    def __init__(self):
        self.auth_url = AUTH_URL
        self.token_url = TOKEN_URL
        self.inventory_url = INVENTORY_BASE_URL
        self.encoded_credentials = encoded_credentials
        self.auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.merchant_loc_key = None
        self.access_token = None
        self.refresh_token = None


    # def get_auth_code(self):
    #     auth_response = requests.get(url=AUTH_URL)
    #     return auth_response

    def get_access_token(self, auth_code):
        payload = {
            "grant_type": "authorization_code",
            "redirect_uri": "Albert_Terc-AlbertTe-Resell-zeijgqsp",
            "code": auth_code
        }
        token_response = requests.post(url=TOKEN_URL, headers=self.auth_headers, auth=encoded_credentials, data=payload)
        self.access_token = token_response.json()['access_token']
        self.refresh_token = token_response.json()['refresh_token']

        return token_response.json()

    def set_access_token(self, access_token):
        self.access_token = access_token

    def refresh_access_token(self, refresh_token):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        token_response = requests.post(url=TOKEN_URL, headers=self.auth_headers, auth=encoded_credentials, data=payload)
        self.access_token = token_response.json()['access_token']
        return token_response.json()

    def create_inventory_location(self, merchant_loc_key, address_line1, address_line2, city, state, zipcode, country):
        endpoint = "/location/"

        inventory_url = f"{self.inventory_url}{endpoint}{merchant_loc_key}"

        json_headers = {
            "Content-Language": "en-US",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
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
        response = requests.post(url=inventory_url, headers=json_headers, json=merchant_location_data)
        self.merchant_loc_key = merchant_loc_key
        if not response.ok:
            pass
        else:
            return response.json()

    def get_inventory_locations(self):
        endpoint = "/location"
        location_url = self.inventory_url + endpoint
        token_header = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url=location_url, headers=token_header)
        return response.json()

    def create_inventory_item(self, sku, item_condition, quantity, title, image_urls, aspects):
        endpoint = "/inventory_item/"
        item_url = self.inventory_url + endpoint + sku

        header = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Language": "en-US",
            "Content-Type": "application/json"
        }

        item_data = {
            "condition": item_condition,
            "packageWeightAndSize": {
                "dimensions": {
                    "height": 6,
                    "length": 2,
                    "width": 1,
                    "unit": "INCH"
                },
                "weight": {
                    "value": 1,
                    "unit": "POUND"
                }
            },
            "availability": {
                "shipToLocationAvailability": {
                    "quantity": quantity
                }
            },
            'product': {
                "title": title,
                "imageUrls": ["https://i.sandbox.ebayimg.com/00/s/NzM4WDEzMTI=/z/FBAAAOSwfkxi8xTL/$_1.JPG?set_id=2"],
                "aspects": aspects
            }
        }

        response = requests.put(item_url, headers=header, json=item_data)
        try:
            return response.json()
        except JSONDecodeError:
            return response.status_code

    def get_inventory_items(self):
        endpoint = "/inventory_item"
        items_url = self.inventory_url + endpoint
        header = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(items_url, headers=header)
        return response.json()

    """policy_type must be 'fulfillment', 'return', or 'payment'"""
    def get_account_policies(self, policy_type: str):
        account_api_url = f"https://api.sandbox.ebay.com/sell/account/v1/{policy_type}_policy"
        token_header = {
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {
            "marketplace_id": "EBAY_US"
        }
        response = requests.get(account_api_url, params=params, headers=token_header)
        return response.json()

    def extract_policy_id(self, policy_type):
        policy_json = self.get_account_policies(policy_type)
        return policy_json[f"{policy_type}Policies"][0][f"{policy_type}PolicyId"]


    def create_offer(self, account_policies, sku, quantity, offer_description, offer_price):
        endpoint = "/offer"
        offer_url = self.inventory_url + endpoint

        header = {
            "Content-Language": "en-US",
            "Authorization": f"Bearer {self.access_token}"
        }

        offer_data = {
            "sku": sku,
            "marketplaceId": "EBAY_US",
            "format": "FIXED_PRICE",
            "availableQuantity": quantity,
            "categoryId": "30120",
            "listingDescription": offer_description,
            "listingPolicies": {
                "fulfillmentPolicyId": account_policies['fulfillmentPolicyId'],
                "paymentPolicyId": account_policies['paymentPolicyId'],
                "returnPolicyId": account_policies['returnPolicyId']
            },
            "pricingSummary": {
                "price": {
                    "currency": "USD",
                    "value": str(offer_price)
                }
            },
            "quantityLimitPerBuyer": 1,
            "includeCatalogProductDetails": True,
            "merchantLocationKey": self.merchant_loc_key
        }

        response = requests.post(offer_url, headers=header, json=offer_data)
        return response.json()

    def publish_offer(self, offer_id):
        endpoint = f"/offer/{offer_id}/publish"
        publish_url = self.inventory_url + endpoint
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(publish_url, headers=headers)
        return response.json()