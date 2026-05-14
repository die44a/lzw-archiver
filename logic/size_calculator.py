from pathlib import Path

class SizeCalculator():
    def __init__(self):
        pass
    
    def calculate(self, path : Path | str) -> int:
        """Calculates file/directory size in KBs

        Args:
            path (Path | str): path to the file/directory for size calculation

        Returns:
            int: size of file/directory in KBs
        """
        return 0