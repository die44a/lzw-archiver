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
