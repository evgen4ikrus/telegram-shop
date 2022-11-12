import requests
from environs import Env


# def get_products(moltin_access_token):
#     headers = {
#         'Authorization': f'Bearer {moltin_access_token}',
#     }
#     response = requests.get('https://api.moltin.com/v2/products', headers=headers)
#     response.raise_for_status()
#     return response.json()


def get_products(moltin_access_token):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
        'EP-Channel': 'web store'
    }
    response = requests.get('https://api.moltin.com/pcm/products/', headers=headers)
    response.raise_for_status()
    products = response.json()['data']
    return products


def get_moltin_access_token(client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token


def create_user_cart(moltin_access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']


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
            'quantity': quantity,
        }
    }
    response = requests.post(
        url=url,
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def get_cart_items(moltin_access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
        'EP-Channel': 'web store'
    }
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
        'EP-Channel': 'web store'
    }
    response = requests.get(f'https://api.moltin.com/pcm/products/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def main():
    env = Env()
    env.read_env()
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    motlin_client_secret = env('MOLTIN_CLIENT_SECRET')

    cart_id = 'abc'

    moltin_access_token = get_moltin_access_token(moltin_client_id, motlin_client_secret)
    products = get_products(moltin_access_token)
    # print(products)
    product = products[1]
    product_id = product['id']
    print(product)
    # get_product(moltin_access_token, product_id)
    # print(create_user_cart(moltin_access_token, cart_id))

    # add_product_to_cart(moltin_access_token, product_id, cart_id, 2)
    # print(get_cart_items(moltin_access_token, cart_id))


if __name__ == '__main__':
    main()
