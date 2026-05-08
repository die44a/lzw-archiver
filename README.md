LZW archiver. Version 0.1
Author: Dima Borisov (dim4ig2007@gmail.com)


Description:
This application is a compression utility designed to encode and decode files and directories. 
It utilizes the Lempel–Ziv–Welch (LZW) algorithm, a universal lossless data compression method.


Requirements:
* Python version greater than 3.10


Composition:
* Console version: clzw.py
* Logic: logic/
* Tests: tests/
  You can execute all tests in one go using the runtests.sh (bash needed)


Console version
Launch help: python clzw.py --help
Launch example: python clzw.py -c example.txt


implementation details:

- `clzw.py`:
    - Parses command line arguments
    - Validates inputs
    - Handles safe overwriting
    - generates a free output name when not provided
    - removes old target in force mode
    - Coordinates full pipeline using temporary files:
        - compression: `TarPacker.pack(...)` -> `LZWArchiver.encode(...)`
        - extraction: `LZWArchiver.decode(...)` -> `TarPacker.unpack(...)`

- `logic/lzw.py`:
  - implements LZW encode/decode
  - Uses 2-byte codes (`CODE_SIZE = 2`, big-endian order)
  - Writes `b"LZW"` signature to output and validates it on decode
  - Dictionary starts with 256 single-byte entries and grows up to `max_dict_size`
    (default `4096`, hard limit `65535`)
    
- `logic/packer.py`:
  - `TarPacker.pack(...)` packs file or directory into `.tar`
  - `TarPacker.unpack(...)` restores archive content with `tarfile.extractall(...)`

- `logic/constants.py` stores all algorithm-related constants in one place.