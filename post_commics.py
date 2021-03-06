import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv


class VKError(Exception):
    pass


def get_random_comics_xkcd_number():
    random_comics_url = "https://xkcd.com/info.0.json"
    response = requests.get(random_comics_url)
    response.raise_for_status()
    last_comics_number = response.json()['num']
    comics_number = random.randint(1, last_comics_number)
    return comics_number


def get_url_and_comment_from_xkcd(comics_number):
    url_xkcd = f"https://xkcd.com/{comics_number}/info.0.json"
    response = requests.get(url_xkcd)
    response.raise_for_status()
    respone_xkcd = response.json()
    comics_url = respone_xkcd["img"]
    comics_comment = respone_xkcd['alt']
    return comics_url, comics_comment


def save_comics_picture(image_url, picture_pass):
    Path(picture_pass).mkdir(parents=True, exist_ok=True)
    filename = Path(picture_pass, "comics.png")
    response = requests.get(image_url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


def check_vk_api(vk_response):
    if "error" in vk_response:
        raise VKError


def upload_picture_to_vk_server(token, group_id, path_to_pic):
    upload_server_url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload_upload = {
        "access_token": token,
        "group_id": group_id,
        "v": 5.131
    }
    response = requests.get(upload_server_url, params=payload_upload)
    response.raise_for_status()
    upload_server_response = response.json()
    check_vk_api(upload_server_response)
    url_for_upload_comics = upload_server_response['response']['upload_url']

    with open(path_to_pic, 'rb') as file:
        files = {
            'photo': file,
            "group_id": group_id
        }
        post_picture = requests.post(url_for_upload_comics, files=files)
        post_picture.raise_for_status()
        uploading_picture = post_picture.json()
        check_vk_api(uploading_picture)
        return uploading_picture


def save_picture_vk(picture, comment, token, group_id, user_id):
    vk_save_picture_url = "https://api.vk.com/method/photos.saveWallPhoto"
    payload_safe_photo = {
        "user_id": user_id,
        "group_id": group_id,
        'hash': picture['hash'],
        "photo": picture['photo'],
        'server': picture['server'],
        "caption": comment,
        "access_token": token,
        "v": 5.131,

    }
    response = requests.post(vk_save_picture_url, params=payload_safe_photo)
    response.raise_for_status()
    vk_safe_photo = response.json()
    check_vk_api(vk_safe_photo)
    picture_id = vk_safe_photo['response'][0]['id']

    return picture_id


def get_publish_comics_on_the_wall(image_id, comment, token, group_id):
    vk_public_photo = "https://api.vk.com/method/wall.post"
    payload_post_photo = {
        "owner_id": -int(group_id),
        "attachments": f"photo4025765_{image_id}",
        "from_group": 1,
        "message": comment,
        "access_token": token,
        "v": 5.131

    }
    response = requests.post(vk_public_photo, params=payload_post_photo)
    response.raise_for_status()
    vk_photo_on_wall = response.json()
    check_vk_api(vk_photo_on_wall)


def main():
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    user_id = os.getenv("USER_ID")
    group_id = os.getenv("GROUP_ID")
    path_for_images = "comics"
    path_to_pic = "comics/comics.png"
    comics_number = get_random_comics_xkcd_number()
    comics_url, comics_comment = get_url_and_comment_from_xkcd(comics_number)
    save_comics_picture(comics_url, path_for_images)

    try:
        uploading_comics = upload_picture_to_vk_server(vk_token, group_id, path_to_pic)
        image_id = save_picture_vk(uploading_comics, comics_comment, vk_token, group_id, user_id)
        get_publish_comics_on_the_wall(image_id, comics_comment, vk_token, group_id)

    except requests.HTTPError:
        print("???????????? HTTPError")
    except VKError:
        print("???????????? VKError")
    finally:
        os.remove(path_to_pic)


if __name__ == '__main__':
    main()
