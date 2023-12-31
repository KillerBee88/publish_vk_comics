import requests


def download_comic(url, file_path):
    response = requests.get(url)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)