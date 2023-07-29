import requests
import os
import random
from download_comics import download_comic
from dotenv import load_dotenv


def handle_vk_response(response):
    response_json = response.json()
    if 'error' in response_json:
        error_code = response_json['error']['error_code']
        error_msg = response_json['error']['error_msg']
        raise VKAPIError(f'Ошибка VK API: Код {error_code}, Сообщение: {error_msg}')
    response.raise_for_status()
    

class VKAPIError(Exception):
    pass


def get_random_comic(last_comic_number):
    comic_number = random.randrange(1, last_comic_number, 1)
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    handle_vk_response(response)
    return response.json()


def get_upload_url(access_token, group_id, version):
    params = {
        "group_id": group_id,
        "access_token": access_token,
        "v": version
    }
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=params)
    handle_vk_response(response)
    return response.json()['response']['upload_url']


def upload_photos_to_server(access_token, group_id, version):
    with open('image.png', 'rb') as file:
        url = get_upload_url(access_token, group_id, version)
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
    handle_vk_response(response)
    uploading_photo = response.json()
    return uploading_photo


def save_wall_photo(access_token, group_id, version, server, photo, photo_hash):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    data = {
        "group_id": group_id,
        "photo": photo,
        "server": server,
        "hash": photo_hash,
        "access_token": access_token,
        "v": version
    }
    response = requests.post(url, params=data)
    handle_vk_response(response)
    return response.json()['response'][0]


def post_comic_on_wall_vk(access_token: str, group_id: int, version: str, owner_id: int, media_id: int, message: str) -> dict:
    attachments = f'photo{owner_id}_{media_id}'
    payload = {
        "owner_id": -group_id,
        "group_id": group_id,
        "from_group": True,
        "attachments": attachments,
        "message": message,
        "access_token": access_token,
        "v": version
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=payload)
    handle_vk_response(response)
    return response.json()


def main():
    load_dotenv()
    access_token = os.environ['VK_ACCESS_TOKEN']
    group_id = int(os.environ['VK_GROUP_ID'])
    version = '5.131'
    number_last_comic = 2750
    comic_info = get_random_comic(number_last_comic)
    
    try:
        download_comic(comic_info['img'], 'image.png')
        uploading_photo = upload_photos_to_server(access_token, group_id, version)
        server = uploading_photo['server']
        photo = uploading_photo['photo']
        photo_hash = uploading_photo['hash']
        save_photo = save_wall_photo(access_token, group_id, version, server, photo, photo_hash)
        owner_id = save_photo['owner_id']
        media_id = save_photo['id']
        post_comic_on_wall_vk(access_token, group_id, version, owner_id, media_id, comic_info['alt'])
    except VKAPIError as e:
        print(f"Произошла ошибка VK API: {str(e)}")
    finally:
        os.remove('image.png')


if __name__ == '__main__':
    main()