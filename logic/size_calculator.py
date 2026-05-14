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
        path = Path(path)
        
        if path.is_file:
            return path.stat().st_size
        
        return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())