import tarfile
from pathlib import Path


class TarPacker:
    """The class implementing packing directory into one file
    using tarfile extention (way of packing may be changed if needed)"""

    def __init__(self):
        pass

    def pack(self, input_path: str | Path, output_path: str | Path = None) -> Path:
        """
        Packs a file or directory into a single TAR archive.

        Args:
            input_path: The path to the file or directory to be packed.
            output_path: The path where the resulting archive will be saved.
                If None, the path is generated automatically based on the input name.

        Returns:
            Path: The path to the resulting TAR archive.
        """
        input_path = Path(input_path).resolve()
        output_path = Path(
            output_path or input_path.with_suffix('.tar')).resolve()

        with tarfile.open(output_path, 'w') as tar:
            tar.add(input_path, arcname=input_path.name)

        return output_path

    def unpack(self, input_path: str | Path, output_path: str | Path = None) -> Path:
        """
        Unpacks a TAR archive to the specified directory.

        Args:
            input_path: Path to the .tar file to be unpacked.
            output_path: Path to the destination directory. 
                Defaults to None (current working directory).

        Returns:
            Path: The path to the directory where files were extracted.
        """
        input_path = Path(input_path).resolve()
        output_path = Path(output_path or input_path.stem).resolve()

        with tarfile.open(input_path, 'r') as tar:
            tar.extractall(path=output_path, filter='data')

            return output_path
