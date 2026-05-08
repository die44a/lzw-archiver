from enum import Enum
from pathlib import Path
from typing import BinaryIO, Iterator
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
    """The class implementing LZM archiver"""

    def __init__(self, max_dict_size=DEFAULT_MAX_DICT):
        self.max_dict_size = min(max_dict_size, DICT_SIZE_LIMIT)

    def encode(self, input_path: str | Path,
               output_path: str | Path = None) -> None:
        """Encodes input file content using LZW algorithm
        Args:
            input_path (str | Path): Path to the file to encode
            output_path (str | Path, optional): Path to the file for output encoded data. If None or not exists generates new file itself

        Raises:
            FileNotFoundError: If input file was not found
            RuntimeError: If something went wrong
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file doesn't exist: {input_path}")

        output_path = Path(output_path or
                           input_path.with_suffix(input_path.suffix + ".lzw"))
        try:
            with (open(input_path, 'rb') as input_file,
                  open(output_path, 'wb') as output_file):
                codes = self._bytes_to_codes(self._read_bytes(input_file))

                header = b'LZW'
                output_file.write(header)

                for code in codes:
                    output_file.write(code.to_bytes(CODE_SIZE, BYTE_ORDER))
        except Exception as e:
            if output_path.exists:
                output_path.unlink()
            raise RuntimeError(f"LZW encoding failed: {e}")

    def decode(self, input_path: str | Path,
               output_path: str | Path = None) -> None:
        """Decodes input file content using LZW algorithm

        Args:
            input_path (str | Path): Path to the file to decode
            output_path (str | Path, optional): Path to the file for output decoded data. If None or not exists generates new file itself

        Raises:
            FileNotFoundError: If input file was not found
            ValueError: if input file has no .lzw extention
            RuntimeError: if someting went wrong
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file doesn't exist: {input_path}")

        if input_path.suffix != '.lzw':
            raise ValueError(f"File {input_path} must have .lzw extension")

        if not output_path:
            original_name = input_path.stem
            output_path = input_path.parent / f"decoded_{original_name}"

        try:
            with (open(input_path, 'rb') as input_file,
                  open(output_path, 'wb') as output_file):
                header = input_file.read(3)
                if header != b"LZW":
                    raise ValueError(f"File {input_file} has wrong metadata")

                bytes = self._codes_to_bytes(self._read_codes(input_file))

                for byte in bytes:
                    output_file.write(byte)
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"LZW decoding failed: {e}")

    @staticmethod
    def _init_dict(mode: DictMode) -> dict[bytes, int] | dict[int, bytes]:
        """Initializes dictionary for encoding and decoding based on mode"""
        if mode == DictMode.ENCODE:
            return {bytes([i]): i for i in range(256)}
        elif mode == DictMode.DECODE:
            return {i: bytes([i]) for i in range(256)}
        else:
            raise ValueError("Invalid mode")

    @staticmethod
    def _read_bytes(input_file: BinaryIO) -> Iterator[bytes]:
        """Reads bytes from the file one by one"""
        while (byte := input_file.read(1)):
            yield byte

    def _bytes_to_codes(self, bytes_iter: Iterator[bytes]) -> Iterator[int]:
        """Transforms bytes sequence into codes sequence"""
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
    def _read_codes(input_file: BinaryIO) -> Iterator[int]:
        """Reads codes from the file (each code takes CODE_SIZE in te file)"""
        while (code := input_file.read(CODE_SIZE)):
            if len(code) < CODE_SIZE:
                break

            yield int.from_bytes(code, BYTE_ORDER)

    def _codes_to_bytes(self, codes_iter: Iterator[int]) -> Iterator[bytes]:
        """Transforms codes sequence into bytes sequence"""
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
