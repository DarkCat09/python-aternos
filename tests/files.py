from pathlib import Path
from typing import List

abs_dir = Path(__file__).absolute().parent
samples = abs_dir / 'samples'


def read_sample(name: str) -> List[str]:

    path = samples / name

    if not path.exists():
        return []

    with path.open('rt', encoding='utf-8') as file:
        return file \
            .read() \
            .strip() \
            .replace('\r\n', '\n') \
            .split('\n')
