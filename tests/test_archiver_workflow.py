import filecmp
import random
import shutil
import string
from pathlib import Path

from logic.lzw import LZWArchiver
import pytest

CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR / 'tests_data'
TEST_FILES_LIST = [f for f in DATA_DIR.iterdir() if f.is_file()]


class TestEncodingDecodingDifferentFormats():

    @pytest.fixture
    def archiver(self):
        """Creates archiver object for each test"""
        return LZWArchiver()

    @pytest.fixture
    def input_file(self, request, tmp_path):
        original_path = request.param
        temp_file = tmp_path / original_path.name
        shutil.copy(original_path, temp_file)
        return temp_file

    @pytest.mark.parametrize("input_file", TEST_FILES_LIST, indirect=True)
    def test_archiver(self, archiver, input_file):
        encoded_path = input_file.with_suffix(input_file.suffix + ".lzw")
        archiver.encode(input_file, encoded_path)

        assert encoded_path.exists()

        decoded_path = input_file.parent / f"final_result_{input_file.name}"
        archiver.decode(encoded_path, decoded_path)

        assert decoded_path.exists()
        assert filecmp.cmp(input_file, decoded_path, shallow=False)


class TestEdgeCases():

    @pytest.fixture
    def archiver(self):
        """Creates archiver object for each test"""
        return LZWArchiver()

    def test_input_file_not_exists(self, archiver, tmp_path):
        input_path = tmp_path / "test_input_file_not_exists"
        with pytest.raises(FileNotFoundError):
            archiver.encode(input_path)

        with pytest.raises(FileNotFoundError):
            archiver.decode(input_path)

    def test_file_with_multiple_dots(self, archiver, tmp_path):
        input_path = tmp_path / "my.test.data.txt"
        input_path.write_text("some content")

        encoded = input_path.with_suffix(input_path.suffix + ".lzw")
        archiver.encode(input_path, encoded)

        assert encoded.name == "my.test.data.txt.lzw"

    def test_random_binary_data(self, archiver, tmp_path):
        input_path = tmp_path / "random.bin"
        input_path.write_bytes(bytes(random.getrandbits(8)
                                     for _ in range(100000)))

        encoded = input_path.with_suffix(".lzw")
        decoded = tmp_path / "decoded_random.bin"

        archiver.encode(input_path, encoded)
        archiver.decode(encoded, decoded)

        assert input_path.read_bytes() == decoded.read_bytes()

    def test_wrong_metadata(self, archiver, tmp_path):
        input_path = tmp_path / "wrong_metadata.lzw"
        input_path.write_bytes(b"ABCDEF")

        with pytest.raises(ValueError):
            archiver.decode(input_path)
