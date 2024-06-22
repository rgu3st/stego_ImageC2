import requests
from stegano import stegano


def upload_image(file_path, upload_url):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(upload_url, files=files)
        return response


def send_image(file_path, upload_url):
    response = upload_image(file_path, upload_url)

    if response.status_code == 200:
        print('Image uploaded successfully!')
    else:
        print(f'Failed to upload image. Status code: {response.status_code}')
        print(response.text)


def hide_message(message, file_path)->str:
    steg = stegano()
    hidden_file_path = steg.hide_message(message, file_path)
    return hidden_file_path


if __name__ == '__main__':
    file_path = "steg_in_2.png"
    stego_messgage = "Hello from the other side again! Bwaha!#"
    hidden_file_path = hide_message(stego_messgage, file_path)
    send_image(file_path=hidden_file_path, upload_url="http://127.0.0.1:5000")

