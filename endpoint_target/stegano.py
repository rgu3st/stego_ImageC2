from PIL import Image
import numpy as np
import os

class stegano:
    def __init__(self):
        self.BYTE_LEN = 8
        self.app_folder = "G:\\repos\\ImageC2\\endpoint_target\\enocde_images\\"  # TODO: use the Path library."
        self.terminator = '#'  # This is the terminator for the message TODO: Make a better terminator
        
        os.makedirs(self.app_folder, exist_ok=True)


    def hide_message(self, message:str, filename:str)->str:
        '''Hides a message in the provided image file, using LSB steganography. Returns the filename of the new image.'''
        image1_PIL = Image.open(filename)
        img_array = np.array(image1_PIL)
        img_array = img_array
        message += self.terminator
        message_bytes = message.encode('utf-8') 
        cur_message_byte = 0  
        cur_message_bit = 0
        count = 0
        char_count = 0 
        for row in img_array:
            if char_count == len(message_bytes):
                print("Done encoding.")
                break
            for pixel in row:
                val = 0
                if char_count >= len(message_bytes)-1:
                    break
                while val < 3:
                    bit_value = (message_bytes[cur_message_byte]>>cur_message_bit) % 2
                    if char_count < len(message_bytes):
                        print(f"{bit_value}", end='')
                    if pixel[val] % 2 == 0 and bit_value != 0:  # If the LSB is 0 But the bit to set is a 1
                        pixel[val] |= 1  # Then set as 1, otherwise leave as a zero
                    elif pixel[val] % 2 != 0 and bit_value == 0:  #LSB is 1 but needs to be zero:
                        pixel[val] = pixel[val] - 1  # -1 from an odd number makes LSB 0
                    cur_message_bit = ( cur_message_bit + 1 ) % 8
                    if cur_message_bit == 0:  # If we roll back over from 8, increment the byte 
                        char_count += 1
                        print("  |||  Encoded: " + chr(message_bytes[cur_message_byte]))
                        cur_message_byte += 1
                    val += 1
                    count += 1
                
        filename = self.app_folder + "\\" + filename
        print(f"Done encoding, saving to: {filename}")
        hidden_image_PIL = Image.fromarray(img_array)
        hidden_image_PIL.save(filename)

        return filename


    def unhide_message(self, filename:str)->str:
        '''This function will take a filename and return the message hidden by our hide_message() method.'''
        image1_PIL = Image.open(filename)
        img_array = np.array(image1_PIL)
        img_array = img_array
        num_bytes_to_print = 8
        max_message_len = 200
        message_bytes =  [0]
        cur_message_byte = 0  # I have to manually track this. I think...
        cur_message_bit = 0
        count = 0
        for row in img_array:
            if chr(message_bytes[cur_message_byte]) == self.terminator:
                print(" |||  self.TERMINATOR found. Exiting row. ")
                break
            if len(message_bytes) >= max_message_len:
                print("Max decode message length met. Stopping.")
                break
            for pixel in row:
                val = 0
                if len(message_bytes) >= max_message_len:
                    break
                # Grab the current byte, shift it to make the current bit in the 1s spot and mod
                if chr(message_bytes[cur_message_byte]) == self.terminator:
                    print(" |||  self.TERMINATOR found. Exiting pixel. ")
                    break
                while val < 3:
                    if pixel[val] % 2 == 1:  # If the read value is 1, OR to set the message bit to 1
                        message_bytes[cur_message_byte] |= 1 << cur_message_bit
                        print("1", end="")
                    else:  # Otherwise, leave this bit as 0
                        print("0", end="")
                    cur_message_bit = ( cur_message_bit + 1 ) % self.BYTE_LEN
                    if cur_message_bit == 0:  # If we roll back over from 8, increment the byte 
                        char = chr(message_bytes[cur_message_byte])
                        print("  |||  Decoded: " + char )
                        if char == self.terminator:
                            break
                        cur_message_byte += 1
                        message_bytes.append(0)
                    val += 1
        message_ascii = ''.join(map(chr, message_bytes[0:-2]))
        return message_ascii
