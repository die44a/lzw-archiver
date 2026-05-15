from pathlib import Path
from typing import BinaryIO

PATH_SIZE = 256
FIlE_SIZE_FIELD_SIZE = 8


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
        if output_path.suffix != '.tar':
            raise ValueError(f"File {output_path} must have .tar extension")

        with open(output_path, 'wb') as tar:
            if input_path.is_file():
                self._write_file_to_archive(input_path, input_path, tar)
                return output_path

            for item in input_path.rglob('*'):
                if item.is_file():
                    self._write_file_to_archive(item, input_path.parent, tar)

        return output_path

    def _write_file_to_archive(self, file_path: Path, base_path: Path, archive_stream: BinaryIO):
        path_bt = bytes(
            str(file_path.relative_to(base_path)), encoding='utf-8')
        if len(path_bt) > PATH_SIZE:
            raise ValueError(
                f'File name size must me less or equal to {PATH_SIZE}')
        path_bt = path_bt.ljust(PATH_SIZE, b'\x00')

        file_size_bt = bytes(str(file_path.stat().st_size),
                             encoding='utf-8')
        if len(file_size_bt) > FIlE_SIZE_FIELD_SIZE:
            raise ValueError(
                f'file size must be less or equal to {FIlE_SIZE_FIELD_SIZE}')
        file_size_bt = file_size_bt.ljust(FIlE_SIZE_FIELD_SIZE, b'\x00')

        archive_stream.write(path_bt)
        archive_stream.write(file_size_bt)
        with open(file_path, 'rb') as f_in:
            archive_stream.write(f_in.read())

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
        if input_path.suffix != '.tar':
            raise ValueError(f"File {input_path} must have .tar extension")
        output_path = Path(output_path or input_path.stem).resolve()

        with open(input_path, 'rb') as tar:
            while True:
                if not self._create_file(output_path, tar):
                    break

        return output_path

    def _create_file(self, output: Path, archive_stream: BinaryIO):
        raw_path = archive_stream.read(PATH_SIZE)
        if not raw_path:
            return False

        file_path = raw_path.decode('utf-8').rstrip('\x00')

        file_size = int(archive_stream.read(
            FIlE_SIZE_FIELD_SIZE).decode('utf-8').rstrip('\x00'))

        final_path = output / file_path

        final_path.parent.mkdir(parents=True, exist_ok=True)

        with open(final_path, 'wb') as f:
            f.write(archive_stream.read(file_size))

        return True
