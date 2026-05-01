import pytest
from logic.lzw import LZWArchiver, DictMode


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
