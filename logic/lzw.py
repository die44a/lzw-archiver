"""
A class that implements archiving and unarchiving 
    using the LZW algorithm
"""

from enum import Enum
from pathlib import Path
from .constants import (
    DICT_SIZE_LIMIT, 
    DEFAULT_MAX_DICT, 
    BYTE_ORDER, 
    CODE_SIZE
)

__all__ = ['LZWArchiver']

class DictMode(Enum):
    """
    Dictionary creating modes:
    ENCODE and DECODE for endcoding and decoding files respectively
    """
    ENCODE = 1
    DECODE = 2

class LZWArchiver():
    def __init__(self, max_dict_size=DEFAULT_MAX_DICT):
        self.max_dict_size = min(max_dict_size, DICT_SIZE_LIMIT)
            
    
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
                
        #header = b'LZW' + self.max_dict_size.to_bytes(2, self.BYTE_ORDER)  # TODO: write down file header
        
        with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
            codes = self._bytes_to_codes(self._read_bytes(input_file))

            for code in codes:
                output_file.write(code.to_bytes(CODE_SIZE, BYTE_ORDER))
            
            
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
        
        with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
            bytes = self._codes_to_bytes(self._read_codes(input_file))

            for byte in bytes:
                output_file.write(byte)
                
    @staticmethod            
    def _init_dict(mode: DictMode):
        if mode == DictMode.ENCODE:
            return {bytes([i]): i for i in range(256)}
        elif mode == DictMode.DECODE:
            return {i: bytes([i]) for i in range(256)}
        else:
            raise ValueError("Invalid mode")
                
    @staticmethod
    def _read_bytes(input_file):
        while(byte := input_file.read(1)):
            yield byte
    
    
    def _bytes_to_codes(self, bytes_iter):
        dictionary = self._init_dict(DictMode.ENCODE)
        next_code = 256
        prefix = b''
        
        for byte in bytes_iter:    
            pc = prefix + byte
            if pc in dictionary:
                prefix = pc
                continue
                
            yield dictionary[prefix]
            
            if next_code < self.max_dict_size:
                dictionary[pc] = next_code
                next_code += 1
                
            prefix = byte
        
        if prefix:
            yield dictionary[prefix]
            
    @staticmethod    
    def _read_codes(input_file):
        while(code := input_file.read(CODE_SIZE)):
            yield int.from_bytes(code, BYTE_ORDER)
            
    
    def _codes_to_bytes(self, codes_iter):
        codes_iter = iter(codes_iter)
        try:
            first_code = next(codes_iter)
        except StopIteration:
            return 
        
        dictionary = self._init_dict(DictMode.DECODE)
        next_code = 256
        sequence = dictionary[first_code]
        yield sequence
        
        for code in codes_iter:
            if code in dictionary:
                entry = dictionary[code]
            elif code == next_code:  
                # Rare case when encoder havnt added sequence yet
                # For examole 'aaaaa' encoded output should be ['97', '256', '256']     
                # This only happens if the sequence starts and ends with the same symbol       
                entry = sequence + sequence[:1]
            else:
                raise ValueError(f"Bad compressed code: {code}")
            
            yield entry
            
            if next_code < self.max_dict_size:
                dictionary[next_code] = sequence + entry[:1]
                next_code += 1
            
            sequence = entry   