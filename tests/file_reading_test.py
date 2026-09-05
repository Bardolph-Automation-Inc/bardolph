import tempfile
import unittest
from pathlib import Path


class FileReadingTest(unittest.TestCase):
    def setUp(self):
        self._path: Path = None

    def tearDown(self):
        path = self._path
        if path is not None and path.exists():
            path.unlink()

    def create_temp_file(self, content: str, suffix: str = '') -> Path:
        with tempfile.NamedTemporaryFile(
                suffix=suffix, mode='w+', delete=False) as file:
            file.write(content)
            file.close()
            self._path = Path(file.name)
        return self._path
