import requests
from environs import Env


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


def main():
    env = Env()
    env.read_env()
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    motlin_client_secret = env('MOLTIN_CLIENT_SECRET')

    moltin_access_token = get_moltin_access_token(moltin_client_id, motlin_client_secret)

    headers = {
        'Authorization': f'Bearer {moltin_access_token}'
    }
    response = requests.get('https://api.moltin.com/pcm/products', headers=headers)
    response.raise_for_status()
    print(response.json())


if __name__ == '__main__':
    main()
