"""
A class that implements archiving and unarchiving 
    using the LZW algorithm
"""

from enum import Enum
from pathlib import Path

class DictMode(Enum):
    ENCODE = 1
    DECODE = 2

class LZWArchiver():
    DICT_SIZE_LIMIT = 65535
    DEFAULT_MAX_DICT = 4096
    BYTE_ORDER = 'big'

    def __init__(self, max_dict_size=DEFAULT_MAX_DICT):
        self.max_dict_size = min(max_dict_size, self.DICT_SIZE_LIMIT)
        
        
    def _init_dict(self, mode: DictMode):
        if mode == DictMode.ENCODE:
            return {bytes([i]): i for i in range(256)}
        elif mode == DictMode.DECODE:
            return {i: bytes([i]) for i in range(256)}
        else:
            raise ValueError("Invalid mode")
    
    
    def encode(self, input_path, output_path=None):
        """_summary_
            Encodes file using LZW algorithm
        Args:
            input_file (str): Input file path
            output_file (str, optional): Output file path. If not specified creates new <input_file>.lzw file

        Raises:
            FileNotFoundError: If input file doesn't exist throws
        """
        
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file doesn't exist: {input_path}")
        
        output_path = Path(output_path or input_path.with_suffix(input_path.suffix + ".lzw"))
        dictionary = self._init_dict(DictMode.ENCODE)
        next_code = 256
        
        #header = b'LZW' + self.max_dict_size.to_bytes(2, self.BYTE_ORDER)  # TODO: write down file header
        
        with open(input_path, 'rb') as f, open(output_path, 'wb') as out: # Go throught file byte by byte
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
                    
                out.write(dictionary[prefix].to_bytes(2, self.BYTE_ORDER))    
                
                if next_code < self.max_dict_size:
                    dictionary[pc] = next_code
                    next_code += 1
                    
                prefix = byte
            
            if prefix:
                out.write(dictionary[prefix].to_bytes(2, self.BYTE_ORDER))
            
            
    def decode(self, input_path, output_path=None):
        """_summary_
            Decodes file encoded by LZW algorithm
        Args:
            input_file (str): .lzw file path to decode
            output_file (str, optional): Output file path. If not specified creates new <input_file> file

        Raises:
            FileNotFoundError: If input file doesn't exist throws this exception
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file doesn't exist: {input_path}")
        
        if input_path.suffix != '.lzw':
            raise ValueError(f"File {input_path} must have .lzw extension")
        
        if not output_path:
            original_name = input_path.stem 
            output_path = input_path.parent / f"decoded_{original_name}"
        
        dictionary = self._init_dict(DictMode.DECODE)
        next_code = 256
        
        with open(input_path, 'rb') as f, open(output_path, 'wb') as out:
            
            data = f.read(2)
            if not data:
                return
            
            code = int.from_bytes(data, self.BYTE_ORDER)
            sequence = dictionary[code]
            out.write(sequence)
            
            while True:
                data = f.read(2)
                if not data: 
                    break
                code = int.from_bytes(data, self.BYTE_ORDER)
                                
                if code in dictionary:
                    entry = dictionary[code]
                elif code == next_code:  
                    # Rare case when encoder havnt added sequence yet
                    # For examole 'aaaaa' encoded output should be ['97', '256', '256']     
                    # This only happens if the sequence starts and ends with the same symbol       
                    entry = sequence + sequence[:1]
                else:
                    raise ValueError(f"Bad compressed code: {code}")
                
                out.write(entry)
                
                if next_code < self.max_dict_size:
                    dictionary[next_code] = sequence + entry[:1]
                    next_code += 1
                
                sequence = entry