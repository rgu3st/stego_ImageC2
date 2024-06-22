import requests
from stegano import stegano
import os
import signal
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from time import sleep


SLEEP_TIME = 5
KNOWN_IMAGE_URLS = [str]
DOWNLOAD_COUNTER = 0
DOWNLOAD_LOCATION = r"G:\repos\ImageC2\endpoint_controller\downloads" 

def get_images_from_webpage(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the content of the request with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all image tags
        img_tags = soup.find_all('img')

        # Extract the source URLs of the images
        img_urls = [urljoin(url, img['src']) for img in img_tags if 'src' in img.attrs]

        return img_urls
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []

def get_steg_reponse(url)->list[str]:
    image_urls = get_images_from_webpage(url)
    # print(f"Found images: {image_urls}")
    return image_urls


def download_image(url, file_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # # Write the image content to a file
        # with open(file_path, 'wb') as file:
        #     response.raw.decode_content = True
        #     shutil.copyfileobj(response.raw, file)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")


def check_for_new_images(NoneType=None):
    global DOWNLOAD_COUNTER
    global DOWNLOAD_LOCATION
    imagec2_url = 'http://localhost:5000/'
    all_image_urls = get_steg_reponse(url = imagec2_url)

    if all_image_urls is not None:
        new_images = [url.split('/')[-1] for url in all_image_urls if url.split('/')[-1] not in KNOWN_IMAGE_URLS]
    if len(new_images) > 0:
        print(f"New images:\n { new_images }")
        for filename in new_images:
            file_path = f"{DOWNLOAD_LOCATION}/{filename}"
            download_image(imagec2_url+"/static/uploads/"+filename, file_path)
            check_for_hidden_message(file_path)
            DOWNLOAD_COUNTER += 1
            KNOWN_IMAGE_URLS.append(filename)
    else:
        print("No new images found.")


def check_for_hidden_message(file_path):
    steg = stegano()
    print(f"Checking for hidden message in {file_path}")
    # Decode the hidden message
    message = steg.unhide_message(file_path)
    print(f"Hidden message: {message}")


def init():
    global KNOWN_IMAGE_URLS
    # Create the download directory if it doesn't exist
    os.makedirs(DOWNLOAD_LOCATION, exist_ok=True)
    # And register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    # Populate the known image URLs
    KNOWN_IMAGE_URLS = [filename for filename in os.listdir(DOWNLOAD_LOCATION)]

    

def signal_handler(sig, frame):
    print('Ctrl+C caught. Clean up and exit...')
    exit(0)


if __name__ == '__main__':
    init()
    while True:
        check_for_new_images()
        sleep(SLEEP_TIME)
