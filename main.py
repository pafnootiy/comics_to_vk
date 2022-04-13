import os
import random
import requests
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv


def get_comics_from_xkcd():
    comics_number = random.randint(1, 2606)
    url_xkcd = f"https://xkcd.com/{comics_number}/info.0.json"
    request_xkcd = requests.get(url_xkcd)
    request_xkcd.raise_for_status()
    comics_url = request_xkcd.json()["img"]
    comics_comment = request_xkcd.json()['alt']
    return comics_url, comics_comment


def create_comics_picture(image_url, picture_pass):
    Path(picture_pass).mkdir(parents=True, exist_ok=True)
    filename = Path(picture_pass, "comics.png")
    response = requests.get(image_url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
        file.close()


def upload_picture_to_vk_server(token):
    upload_server_url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload_upload = {
        "access_token": token,
        "group_id": 212659626,
        "v": 5.131
    }
    upload_server_response = requests.get(upload_server_url, params=payload_upload)
    upload_server_response.raise_for_status()
    url_for_upload_comics = upload_server_response.json()['response']['upload_url']

    with open('comics/comics.png', 'rb') as file:
        files = {
            'photo': file,
            "group_id": 212659626
        }
        post_picture = requests.post(url_for_upload_comics, files=files)
        post_picture.raise_for_status()
        uploading_picture = post_picture.json()
        return uploading_picture


def saving_picture_vk(picture, comment, token):
    vk_save_picture_url = "https://api.vk.com/method/photos.saveWallPhoto"
    payload_safe_photo = {
        "user_id": 4025765,
        "group_id": 212659626,
        'hash': picture['hash'],
        "photo": picture['photo'],
        'server': picture['server'],
        "caption": comment,
        "access_token": token,
        "v": 5.131,

    }
    vk_safe_photo = requests.post(vk_save_picture_url, params=payload_safe_photo)
    vk_safe_photo.raise_for_status()
    picture_id = vk_safe_photo.json()['response'][0]['id']
    return picture_id


def public_comics_on_the_wall(id, comment, token):
    vk_public_photo = "https://api.vk.com/method/wall.post"
    payload_post_photo = {
        "owner_id": -212659626,
        "attachments": f"photo4025765_{id}",
        "from_group": 1,
        "message": comment,
        "access_token": token,
        "v": 5.131

    }
    vk_photo_on_wall = requests.post(vk_public_photo, params=payload_post_photo)
    vk_photo_on_wall.raise_for_status()
    os.remove("comics/comics.png")


def main():
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    user_id = os.getenv("USER_ID")
    path_for_images = "comics"
    comics_url = get_comics_from_xkcd()[0]
    comics_comment = get_comics_from_xkcd()[1]
    create_comics_picture(comics_url, path_for_images)
    uploading_comics = upload_picture_to_vk_server(vk_token)
    image_id = saving_picture_vk(uploading_comics, comics_comment, vk_token)
    public_comics_on_the_wall(image_id, comics_comment, vk_token)


if __name__ == '__main__':
    main()
