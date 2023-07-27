import requests


def download_comics(url, file_path):
    response = requests.get(url)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)