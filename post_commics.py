import os
import random
import requests
from pathlib import Path
from dotenv import load_dotenv
from pprint import pprint


def get_random_comics_from_xkcd():
    last_comics_url = "https://xkcd.com/info.0.json"
    last_comics = requests.get(last_comics_url)
    last_comics_number = last_comics.json()['num']
    comics_number = random.randint(1, last_comics_number)
    url_xkcd = f"https://xkcd.com/{comics_number}/info.0.json"
    request_xkcd = requests.get(url_xkcd)
    request_xkcd.raise_for_status()
    respone_xkcd = request_xkcd.json()
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
        file.close()


def upload_picture_to_vk_server(token, group_id):
    upload_server_url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload_upload = {
        "access_token": token,
        "group_id": group_id,
        "v": 5.131
    }
    upload_server_response = requests.get(upload_server_url, params=payload_upload)
    upload_server_response.raise_for_status()
    url_for_upload_comics = upload_server_response.json()['response']['upload_url']

    with open('comics/comics.png', 'rb') as file:
        files = {
            'photo': file,
            "group_id": group_id
        }
        post_picture = requests.post(url_for_upload_comics, files=files)
        post_picture.raise_for_status()
        uploading_picture = post_picture.json()
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
    vk_safe_photo = requests.post(vk_save_picture_url, params=payload_safe_photo)
    vk_safe_photo.raise_for_status()
    picture_id = vk_safe_photo.json()['response'][0]['id']
    return picture_id


def public_comics_on_the_wall(image_id, comment, token, group_id):
    vk_public_photo = "https://api.vk.com/method/wall.post"
    payload_post_photo = {
        "owner_id": -int(group_id),
        "attachments": f"photo4025765_{image_id}",
        "from_group": 1,
        "message": comment,
        "access_token": token,
        "v": 5.131

    }
    vk_photo_on_wall = requests.post(vk_public_photo, params=payload_post_photo)
    vk_photo_on_wall.raise_for_status()

def remove_temporary_photo():
    try:
        with open('comics/comics.png', 'rb') as file:
            file.close()
    finally:
        os.remove("comics/comics.png")


def check_vk_api():
    try:
        vk_url = "https://api.vk.com/method/wall.post"
        vk_response = requests.get(vk_url)
    except requests.HTTPError():
        print("Ошибка сервера")



def main():
    load_dotenv()
    check_vk_api()
    vk_token = os.getenv("VK_TOKEN")
    user_id = os.getenv("USER_ID")
    group_id = os.getenv("GROUP_ID")
    path_for_images = "comics"
    random_comics_from_xkcd = get_random_comics_from_xkcd()
    comics_url = random_comics_from_xkcd[0]
    comics_comment = random_comics_from_xkcd[1]
    save_comics_picture(comics_url, path_for_images)
    uploading_comics = upload_picture_to_vk_server(vk_token, group_id)
    image_id = save_picture_vk(uploading_comics, comics_comment, vk_token, group_id, user_id)
    public_comics_on_the_wall(image_id, comics_comment, vk_token, group_id)
    remove_temporary_photo()



if __name__ == '__main__':
    main()
