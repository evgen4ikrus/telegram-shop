import requests
from environs import Env


def get_all_products(moltin_access_token):
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


def get_cart_items(moltin_access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
        'EP-Channel': 'web store'
    }
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product_by_id(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
        'EP-Channel': 'web store'
    }
    response = requests.get(f'https://api.moltin.com/pcm/products/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product_files(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json',
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


# Доделать получение цены и передать сообщение при клике на товар
# def get_price_books(moltin_access_token):
#     headers = {
#         'Authorization': f'Bearer {moltin_access_token}',
#         'Content-Type': 'application/json',
#         'EP-Channel': 'web store'
#     }
#     response = requests.get('https://api.moltin.com/pcm/pricebooks/2adf5916-5dfe-4b27-9ece-42b3ce9a49d5/prices/f35c9a26-3120-4cc7-9044-37d6749b5e9c', headers=headers)
#     response.raise_for_status()
#     return response.json()


def main():
    env = Env()
    env.read_env()
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    motlin_client_secret = env('MOLTIN_CLIENT_SECRET')

    moltin_access_token = get_moltin_access_token(moltin_client_id, motlin_client_secret)
    products = get_all_products(moltin_access_token)

    product = products[1]
    product_id = product['id']
    # product = get_product_by_id(moltin_access_token, product_id)
    # create_user_cart(moltin_access_token, cart_id)
    # print(product)

    # add_product_to_cart(moltin_access_token, product_id, cart_id, 1)
    # cart_items = get_cart_items(moltin_access_token, cart_id)
    # print(get_price_books(moltin_access_token))


if __name__ == '__main__':
    main()
