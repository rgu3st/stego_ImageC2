from PIL import Image
import numpy as np
import os
from pathlib import Path


# TODO: Encrypt/Decrypt the message before encoding/decoding it.
class stegano:
    def __init__(self, save_folder:Path):
        self.BYTE_LEN = 8
        self.app_folder = save_folder  
        self.terminator = '^'  # This is the terminator for the message TODO: Make a better terminator? Reserve the first 64 LSBs for the length of the message instead?
        self.padding = ''  # This is the padding for the message
        self.start_flag = 'STARTRJAG!'
        self.max_message_len = 820*480*3 / 8 # This is the maximum message byte length that can be encoded in a 820x480 image, seems like a safe enough number for now...
        
        os.makedirs(self.app_folder, exist_ok=True)


    def hide_message(self, message:str, filename:str)->str:
        '''Hides a message in the provided image file, using LSB steganography. Returns the filename of the new image.'''
        if message == "" or not isinstance(message, str):
            print("No message to encode.")
            return None
        if None == message:
            print("No message to encode.")
            return None
        if len(message) > self.max_message_len:
            print(f"Message too long at {len(message)}. Max length is {self.max_message_len}.")
            return None
        
        message = self.start_flag + message + self.padding + self.terminator
        message_bytes = message.encode('utf-8') 
        length = len(message_bytes) 
        # print(f"Encoding message: {message}")
        
        try:
            # print(f"Opening image file: {filename}")
            image1_PIL = Image.open(filename)
        except FileNotFoundError:
            print(f"Could not encode message. File not found: {filename}")
            return None
        img_array = np.array(image1_PIL)
        img_array = img_array
        
        cur_message_byte = 0  
        cur_message_bit = 0
        char_count = 0 
        for row in img_array:
            if cur_message_byte == length:
                break  # Done encoding, break out of outermost loop
            for pixel in row:
                if cur_message_byte == length:
                    break  # Done encoding, break out of middle loop
                val = 0
                while val < 3:
                    bit_value = (message_bytes[cur_message_byte]>>cur_message_bit) % 2
                    if char_count < length:
                        #print(f"{bit_value}", end='')
                        pass
                    if pixel[val] % 2 == 0 and bit_value != 0:  # If the LSB is 0 But the bit to set is a 1
                        pixel[val] |= 1  # Then set as 1, otherwise leave as a zero
                    elif pixel[val] % 2 != 0 and bit_value == 0:  #LSB is 1 but needs to be zero:
                        pixel[val] = pixel[val] - 1  # -1 from an odd number makes LSB 0
                    cur_message_bit = ( cur_message_bit + 1 ) % self.BYTE_LEN
                    if cur_message_bit == 0:  # If we roll back over from 8, increment the byte 
                        char_count += 1
                        # print("  |||  Encoded: " + chr(message_bytes[cur_message_byte]))
                        cur_message_byte += 1
                        if cur_message_byte == length:
                            break  # Done encoding, break out of innermost loop
                    val += 1
                
        filename = self.app_folder / filename
        # print(f"Done encoding, saving to: {filename}")
        hidden_image_PIL = Image.fromarray(img_array)
        hidden_image_PIL.save(filename)

        return filename


    def unhide_message(self, filename:str)->str:
        '''This function will take a filename and return the message hidden by our hide_message() method.'''
        try:
            image1_PIL = Image.open(filename)
        except FileNotFoundError:
            print(f"Could not decode message. File not found: {filename}")
            return None
        img_array = np.array(image1_PIL)
        img_array = img_array
        num_bytes_to_print = 8
        message_bytes =  [0]
        cur_message_byte = 0  # I have to manually track this. I think...
        cur_message_bit = 0
        length = len(self.start_flag) + len(self.padding) + len(self.terminator)
        done = False
        for row in img_array:
            if done:
                break
            if length >= self.max_message_len:
                # print("Max decode message length met. Stopping.")
                break
            for pixel in row:
                val = 0
                if done:
                    break
                while val < 3:
                    if pixel[val] % 2 == 1:  # If the read value is 1, OR to set the message bit to 1
                        message_bytes[cur_message_byte] |= 1 << cur_message_bit
                        # print("1", end="")
                    else:  # Otherwise, leave this bit as 0
                        # print("0", end="")
                        pass
                    cur_message_bit = ( cur_message_bit + 1 ) % self.BYTE_LEN
                    if cur_message_bit == 0:  # If we roll back over from 8, increment the byte 
                        char = chr(message_bytes[cur_message_byte])
                        # print("  |||  Decoded: " + char )
                        if char == self.terminator:
                            done = True
                            break
                        cur_message_byte += 1
                        message_bytes.append(0)
                        length += 1
                    val += 1
        # Finally, take all the bytes and convert them to a string:
        message = ''.join(map(chr, message_bytes[0:]))  # I could use this inside the "if cur_message_bit == 0" block above to check for a longer end-flag, if desired.
        # print(f"Decoded message: {message}")
        # Clear the start and end-flags:
        if not message.startswith(self.start_flag):
            message = ""
        message = message.split(self.start_flag)
        if len(message) < 2:
            message = ""
        else:
            message = message[1]
        message = message.split(self.terminator)
        if len(message) < 2:
            message = ""
        else:
            message = message[0]
        message = message.replace(self.terminator, "")  

        return message
