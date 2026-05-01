from logic.lzw import LZWArchiver, DictMode
from logic.constants import BYTE_ORDER, CODE_SIZE
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


class TestBytesToCodes():

    @pytest.fixture
    def archiver(self):
        return LZWArchiver()

    @pytest.fixture
    def bytes_iter(self, request):
        data = getattr(request, "param", b"")
        return (data[i:i+1] for i in range(len(data)))

    @pytest.mark.parametrize("bytes_iter", [b""], indirect=True)
    def test_if_empty(self, archiver, bytes_iter):
        codes_iter = archiver._bytes_to_codes(bytes_iter)

        assert list(codes_iter) == []

    @pytest.mark.parametrize("bytes_iter, expected",
                             [
                                 (b"a", [97]),
                                 (b"abc", [97, 98, 99]),
                                 (b"abab", [97, 98, 256]),
                                 (b"AAAAA", [65, 256, 256]),
                                 (b"PIKAPIKA", [80, 73, 75, 65, 256, 258]),
                                 (b"PIKACHUPINCHES", [
                                  80, 73, 75, 65, 67, 72, 85, 256, 78, 260, 69, 83])
                             ],
                             indirect=["bytes_iter"])
    def test_bytes_to_codes(self, archiver, bytes_iter, expected):
        codes_iter = archiver._bytes_to_codes(bytes_iter)
        assert list(codes_iter) == expected

    def test_dict_overflow(self):
        a = LZWArchiver(256)

        data = b"ababababab"
        bytes_iter = (data[i:i+1] for i in range(len(data)))

        result = list(a._bytes_to_codes(bytes_iter))
        assert result == [97, 98, 97, 98, 97, 98, 97, 98, 97, 98]


class TestCodesToBytes:

    @pytest.fixture
    def archiver(self):
        return LZWArchiver()

    @pytest.mark.parametrize("codes, expected", [
        ([], b""),
        ([97], b"a"),
        ([97, 98, 99], b"abc"),
        ([97, 98, 256], b"abab"),
        ([97, 256, 257], b"aaaaaa"),
    ])
    def test_codes_to_bytes(self, archiver, codes, expected):
        result = b"".join(archiver._codes_to_bytes(codes))
        assert result == expected

    def test_codes_to_bytes_invalid_code(self, archiver):
        with pytest.raises(ValueError, match="Bad compressed code"):
            list(archiver._codes_to_bytes([97, 300]))

    def test_decode_dict_overflow(self, archiver):
        archiver.max_dict_size = 257

        codes = [97, 98, 256, 256]

        result = b"".join(archiver._codes_to_bytes(codes))

        assert result == b"ababab"
