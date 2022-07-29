import unittest
# import ebay_api
from io import StringIO
from ebay_api import create_inventory_item, create_offer, create_listing
from ebay_rest import Error
from unittest.mock import patch
import ebay_rest.a_p_i as ebay_api


class TestEbayApi(unittest.TestCase):
    def setUp(self):
        self.api = ebay_api.API(application='sandbox_1', user='sandbox_1', header='US')
        self.item_phone_data = {
            "product": {
                "title": "Motorola G Power",
                "description": "Smartphone from 2020. Used, but in great condition. No scratches or marks.",
                "aspects": {
                    "Features": ["3D Depth Sensor", "Accelerometer"],
                    "Operating System": ["Android"]
                },
                "brand": "Motorola",
                "mpn": "Moto G Power",
                "imageUrls": [
                    "https://i.ebayimg.com/images/g/sncAAOSwfzBiOYiR/s-l1600.jpg",
                    "https://i.ebayimg.com/images/g/S0sAAOSwQaFiOYiS/s-l500.jpg"
                ]
            },
            "condition": "USED_GOOD",
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
                    "quantity": 1
                }
            }
        }
        self.item_phone_sku = "MO20USBLVE"
        self.item_record_data = {
            "availability": {
                "pickup_at_location_availability": None,
                "ship_to_location_availability": {
                    "allocation_by_format": {
                        "auction": 0,
                        "fixed_price": 1
                    },
                    "availability_distributions": None,
                    "quantity": 1
                }
            },
            "condition": "USED_GOOD",
            "condition_description": None,
            "group_ids": None,
            "inventory_item_group_keys": None,
            "locale": "en_US",
            "package_weight_and_size": {
                "dimensions": {
                    "height": 6.0,
                    "length": 2.0,
                    "unit": "INCH",
                    "width": 1.0
                },
                "package_type": None,
                "weight": {
                    "unit": "POUND",
                    "value": 1.0
                }
            },
            "product": {
                "aspects": "{'Features': ['3D Depth Sensor', 'Accelerometer'], 'Operating System': ['Android']}",
                "brand": "Motorola",
                "description": "Smartphone from 2020. Used, but in great condition. No scratches or marks.",
                "ean": None,
                "epid": None,
                "image_urls": [
                    "https://i.ebayimg.com/images/g/sncAAOSwfzBiOYiR/s-l1600.jpg",
                    "https://i.ebayimg.com/images/g/S0sAAOSwQaFiOYiS/s-l500.jpg"
                ],
                "isbn": None,
                "mpn": "Moto G Power",
                "subtitle": None,
                "title": "Motorola G Power",
                "upc": None,
                "video_ids": None
            },
            "sku": "MO20USBLVE"
        }
        self.policy_ids = {
            'fulfillmentPolicyId': '6196611000',
            'paymentPolicyId': '6196616000',
            'returnPolicyId': '6196618000'
        }

        self.offer_data = {
            "sku": self.item_phone_sku,
            "marketplaceId": "EBAY_US",
            "format": "FIXED_PRICE",
            "availableQuantity": 1,
            "categoryId": "30120",
            "listingDescription": "test",
            "listingPolicies": {
                "fulfillmentPolicyId": "3*********0",
                "paymentPolicyId": "3*********0",
                "returnPolicyId": "3*********0"
            },
            "pricingSummary": {
                "price": {
                    "currency": "USD",
                    "value": "272.17"
                }
            },
            "quantityLimitPerBuyer": 2,
            "includeCatalogProductDetails": True,
        }

        self.seller_location_data = {
            "location": {
                "address": {
                    "addressLine1": "625 6th Ave",
                    "addressLine2": "Fl 2",
                    "city": "New York",
                    "stateOrProvince": "NY",
                    "postalCode": "10011",
                    "country": "US"
                }
            },
            "locationInstructions": "Items ship from here.",
            "name": "Cell Phone Vendor 6th Ave",
            "merchantLocationStatus": "ENABLED",
            "locationTypes": [
                "STORE"
            ]
        }
        self.seller_location_key = "NYCLOC6TH"

    def tearDown(self):
        self.api = None
        self.item_phone_data = None
        self.item_phone_sku = None
        self.item_record_data = None
        self.policy_ids = None
        self.offer_data = None
        self.seller_location_data = None
        self.seller_location_key = None

    def test_create_inventory_item(self):
        with self.assertRaises(Error):
            create_inventory_item(self.api, "fake item data", "fake sku")
            create_inventory_item(self.api, None, None)

        if self.assertEqual(create_inventory_item(self.api, self.item_phone_data, self.item_phone_sku), None):
            self.assertDictEqual(self.api.sell_inventory_get_inventory_item(self.item_phone_sku), self.item_record_data)

    def test_create_offer(self):
        with self.assertRaises(TypeError):
            create_offer(self.api, "fake policy data", "fake offer data")

        self.assertEqual(create_offer(self.api, self.policy_ids, self.offer_data), '8204980010')

    def test_create_listing(self):
        start_msg = "Starting...\n"
        bad_request_error = "Error 99400 is Bad Request b'{\"errors\":[{\"errorId\":2004,\"domain\":\"ACCESS\"," \
                            "\"category\":\"REQUEST\",\"message\":\"Invalid request\",\"longMessage\":\"The request " \
                            "has errors. For help, see the documentation for this API.\",\"parameters\":[{" \
                            "\"name\":\"reason\",\"value\":\"Can not instantiate value of type [simple type, " \
                            "class com.ebay.raptor.slrinvapi.app.entities.InventoryItem] from JSON String; no " \
                            "single-String constructor/factory method\"}]}]}'. "

        with patch('sys.stdout', new=StringIO()) as mock_out:
            create_listing(self.api, "fake sku", "fake item data", "fake offer data", "fake loc data", "fake loc key")
            self.assertEqual(start_msg + bad_request_error, mock_out.getvalue())

        listing_success = """{'listing_id': '110551073730', 'warnings': [{'category': 'REQUEST', 'domain': 'API_INVENTORY', 'error_id': 25402, 'input_ref_ids': None, 'long_message': None, 'message': 'System warning. Offer(s) are already published, please enter a new unpublished offer.', 'output_ref_ids': None, 'parameters': [{'name': 'offerId', 'value': '8204980010'}], 'subdomain': 'Selling'}]} 
        Here's the link to your eBay listing:
        https://www.sandbox.ebay.com/itm/110551073730"""

        with patch('sys.stdout', new=StringIO()) as mock_out:
            create_listing(self.api, self.item_phone_sku, self.item_phone_data, self.offer_data,
                           self.seller_location_data, self.seller_location_key)

            self.assertEqual(mock_out.getvalue(), listing_success)


if __name__ == '__main__':
    unittest.main()
