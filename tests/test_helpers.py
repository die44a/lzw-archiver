from pathlib import Path
from logic.lzw import LZWArchiver, DictMode
from logic.constants import BYTE_ORDER, CODE_SIZE
import os
import pytest


class TestDictInitializer():

    @pytest.fixture
    def archiver(self):
        """Creates archiver object for each test"""
        return LZWArchiver()

    @pytest.mark.parametrize("mode", [DictMode.ENCODE, DictMode.DECODE])
    def test_init_dict_size(self, archiver: LZWArchiver, mode):
        dictionary = archiver._init_dict(mode)
        assert len(dictionary) == 256

    def test_init_dict_encode_values(self, archiver: LZWArchiver):
        dictionary = archiver._init_dict(DictMode.ENCODE)
        for i, b in enumerate(dictionary):
            assert i == dictionary[b]

    def test_init_dict_decode_values(self, archiver: LZWArchiver):
        dictionary = archiver._init_dict(DictMode.DECODE)
        for i, b in enumerate(dictionary):
            assert bytes([i]) == dictionary[b]

    def test_init_dict_incorrect_mode(self, archiver: LZWArchiver):
        with pytest.raises(ValueError) as excinfo:
            archiver._init_dict('FOO')
        assert "Invalid mode" in str(excinfo.value)

    def test_init_dict_creates_new_object(self, archiver: LZWArchiver):
        dict1 = archiver._init_dict(DictMode.ENCODE)
        dict2 = archiver._init_dict(DictMode.ENCODE)
        assert dict1 is not dict2
        dict1[b'new'] = 999
        assert b'new' not in dict2


class TestReadBytes():

    @pytest.fixture
    def archiver(self):
        return LZWArchiver()

    @pytest.fixture
    def binary_file(self, tmp_path, request):
        data = getattr(request, "param", b"")
        file_path = tmp_path / "test_file.bin"
        file_path.write_bytes(data)
        return file_path

    @pytest.mark.parametrize("binary_file", [bytes(range(256))], indirect=True)
    def test_read_binary_file(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = list(archiver._read_bytes(f))
        assert len(result) == 256
        for i, b in enumerate(result):
            assert bytes([i]) == b

    @pytest.mark.parametrize("binary_file", [b""], indirect=True)
    def test_read_empty_file(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = list(archiver._read_bytes(f))
        assert len(result) == 0

    @pytest.mark.parametrize("binary_file", [b"A" * 10000], indirect=True)
    def test_read_large_data(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = archiver._read_bytes(f)

            count = 0
            for b in result:
                assert b == b"A"
                count += 1

        assert count == 10000

    @pytest.mark.parametrize("binary_file", [b"\x00\xff\x1a\x0a\x0d"], indirect=True)
    def test_read_special_symbols(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = list(archiver._read_bytes(f))

        assert result == [b"\x00", b"\xff", b"\x1a", b"\x0a", b"\x0d"]


class TestReadCodes():

    @pytest.fixture
    def archiver(self):
        return LZWArchiver()

    @pytest.fixture
    def binary_file(self, tmp_path, request):
        data = getattr(request, "param", b"")
        file_path = tmp_path / "test_file.bin"
        file_path.write_bytes(data)
        return file_path

    @pytest.mark.parametrize("binary_file", [b"".join([c.to_bytes(CODE_SIZE, BYTE_ORDER) for c in range(256)])], indirect=True)
    def test_read_binary_file(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = list(archiver._read_codes(f))

        assert result == list(range(256))

    @pytest.mark.parametrize("binary_file", [b""], indirect=True)
    def test_read_empty_file(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = list(archiver._read_codes(f))

        assert result == []

    @pytest.mark.parametrize("binary_file", [b"\x01\x02"], indirect=True)
    def test_read_byte_order(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = list(archiver._read_codes(f))

        expected = 258 if BYTE_ORDER == 'big' else 513
        assert result == [expected]

    @pytest.mark.parametrize("binary_file", [b"\x01\x02\x03"], indirect=True)
    def test_read_broken_file(self, archiver, binary_file):
        """Should not read last code if it's shorter than CODE_SIZE"""
        with open(binary_file, "rb") as f:
            result = list(archiver._read_codes(f))

        assert result == [258]

    @pytest.mark.parametrize("binary_file", [b"".join([(97).to_bytes(CODE_SIZE, BYTE_ORDER)]) * 5000], indirect=True)
    def test_read_large_data(self, archiver, binary_file):
        with open(binary_file, "rb") as f:
            result = archiver._read_codes(f)

            count = 0
            for code in result:
                assert code == 97
                count += 1

        assert count == 5000
