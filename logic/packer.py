import tarfile
from pathlib import Path


class TarPacker:
    """The class implementing packing directory into one file 
    using tarfile extention (way of packing may be changed if needed)"""

    def __init__(self):
        pass

    def pack(self, input_path: str | Path, output_path: str | Path) -> Path:
        input_path = Path(input_path).resolve()
        output_path = Path(output_path).resolve().with_suffix('.tar')

        with tarfile.open(output_path, 'w') as tar:
            tar.add(input_path, arcname=input_path.name)

        return output_path

    def unpack(self, input_path: str | Path, output_path: str | Path) -> Path:
        input_path = Path(input_path).resolve()
        output_path = Path(output_path).resolve()

        with tarfile.open(input_path, 'r') as tar:
            tar.extractall(path=output_path, filter="data")

        return output_path


if __name__ == "__main__":
    packer = TarPacker()
    packer.pack('lorem_ipsum.txt', 'lorem_ipsum.tar')
    packer.unpack('lorem_ipsum.tar', 'new_lorem')
