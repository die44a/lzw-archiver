import filecmp
from pathlib import Path
import shutil
from logic.packer import TarPacker
import pytest

CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR / 'tests_data'
TEST_FILES_LIST = [f for f in DATA_DIR.iterdir() if f.is_file()]


class TestPackerWorkflow():
    @pytest.fixture
    def packer(self):
        """Creates packer object for each test"""
        return TarPacker()

    @pytest.fixture
    def input_path(self, request, tmp_path):
        original_path = request.param
        temp_file = tmp_path / original_path.name
        shutil.copy(original_path, temp_file)
        return temp_file

    @pytest.mark.parametrize("input_path", TEST_FILES_LIST, indirect=True)
    def test_packer_packs_unpacks(self, packer, input_path):
        packed_path = input_path.with_suffix('.tar')
        packer.pack(input_path, packed_path)

        assert packed_path.exists()

        unpacked_path = input_path.parent / f"unpacked_path_{input_path.name}"
        packer.unpack(packed_path, unpacked_path)

        assert unpacked_path.exists()
        assert self.compare(input_path, unpacked_path)

    from pathlib import Path

    def compare(self, a: Path, b: Path) -> bool:
        a, b = Path(a), Path(b)

        a_is_file = a.is_file()
        b_is_file = b.is_file()

        if a_is_file and b_is_file:
            return filecmp.cmp(a, b, shallow=False)

        if a.is_dir() and b.is_dir():
            return self.compare_dirs(a, b)

        if a_is_file and b.is_dir():
            b_items = list(b.iterdir())
            if len(b_items) == 1:
                return self.compare(a, b_items[0])
            return False

        if b.is_file() and a.is_dir():
            a_items = list(a.iterdir())
            if len(a_items) == 1:
                return self.compare(a_items[0], b)
            return False

        return False

    def compare_dirs(self, d1: Path, d2: Path) -> bool:
        d1, d2 = Path(d1), Path(d2)

        cmp = filecmp.dircmp(d1, d2)

        if cmp.left_only or cmp.right_only or cmp.funny_files:
            return False

        _, mismatch, errors = filecmp.cmpfiles(
            d1, d2, cmp.common_files, shallow=False)

        if mismatch or errors:
            return False

        for subdir in cmp.common_dirs:
            if not self.compare_dirs(d1 / subdir, d2 / subdir):
                return False

        d1_items = list(d1.iterdir())
        d2_items = list(d2.iterdir())

        if len(d1_items) == 1 and d1_items[0].is_dir():
            return self.compare_dirs(d1_items[0], d2)

        if len(d2_items) == 1 and d2_items[0].is_dir():
            return self.compare_dirs(d1, d2_items[0])

        return True
