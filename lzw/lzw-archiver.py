"""
A class that implements archiving and unarchiving 
    using the LZW algorithm
"""

import os

class LZWArchiver():

    DICT_SIZE_LIMIT = 65535

    def __init__(self, max_dict_size=4096):
        self.max_dict_size = min(max_dict_size, self.DICT_SIZE_LIMIT)
    
    def encode(self, input_file, output_file=None):
        """_summary_
            Encodes file using LZW algorithm
        Args:
            input_file (str): Input file path
            output_file (str, optional): Output file path. If not specified creates new <input_file>.lzw file

        Raises:
            FileNotFoundError: If input file doesn't exist throws
        """
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file doesn't exist: {input_file}")
        
        if output_file is None:
            output_file = input_file + ".lzw"
        
        dictionary = {bytes([i]) : i for i in range(256)}
        next_code = 256
        
        #header = b'LZW' + self.max_dict_size.to_bytes(2, 'big')  # TODO: write down file header
        
        with open(input_file, 'rb') as f, open(output_file, 'wb') as out: # Go throught file byte by byte
            #out.write(header) TODO: write down file header
        
            prefix = b''
            while True:
                byte = f.read(1)
                if not byte:
                    break
                
                pc = prefix + byte
                if pc in dictionary:
                    prefix = pc
                    continue
                    
                out.write(dictionary[prefix].to_bytes(2, 'big'))    
                
                if next_code < self.max_dict_size:
                    dictionary[pc] = next_code
                    next_code += 1
                    
                prefix = byte
            
            if prefix:
                out.write(dictionary[prefix].to_bytes(2, 'big'))
            
            
    def decode(self, input_file, output_file=None):
        """_summary_
            Decodes file encoded by LZW algorithm
        Args:
            input_file (str): .lzw file path to decode
            output_file (str, optional): Output file path. If not specified creates new <input_file> file

        Raises:
            FileNotFoundError: If input file doesn't exist throws this exception
        """
        pass