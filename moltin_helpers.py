import requests
from datetime import datetime

MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT = None, None


def get_all_products(moltin_access_token):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get('https://api.moltin.com/catalog/products/', headers=headers)
    response.raise_for_status()
    products = response.json()['data']
    return products


def get_moltin_access_token(client_id, client_secret):
    global MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT
    if MOTLIN_ACCESS_TOKEN:
        left_time = TOKEN_CREATED_AT - datetime.now().timestamp()
        minimum_seconds = 30
        if left_time > minimum_seconds:
            return MOTLIN_ACCESS_TOKEN
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    raw_response = response.json()
    MOTLIN_ACCESS_TOKEN = raw_response['access_token']
    TOKEN_CREATED_AT = raw_response['expires']
    return MOTLIN_ACCESS_TOKEN


def create_user_cart(moltin_access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}', headers=headers)
    response.raise_for_status()


def add_product_to_cart(moltin_access_token, product_id, cart_id, quantity):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
    }
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    payload = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': int(quantity),
        }
    }
    response = requests.post(
        url=url,
        headers=headers,
        json=payload
    )
    response.raise_for_status()


def get_cart_items(moltin_access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product_by_id(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(f'https://api.moltin.com/catalog/products/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product_files(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(f'https://api.moltin.com/pcm/products/{product_id}/relationships/files', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_file_by_id(moltin_access_token, file_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def delete_product_from_cart(moltin_access_token, cart_id, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}', headers=headers)
    response.raise_for_status()


def create_customer(moltin_access_token, name, email):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        'data': {
            'name': name,
            'email': email,
            'type': 'customer',
        }
    }
    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=payload)
    response.raise_for_status()
