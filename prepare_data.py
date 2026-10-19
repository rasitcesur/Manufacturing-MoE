"""Unpack the provided synthetic training data before training."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT/'training_data.zip'
EXPECTED=(ROOT/'data/robotics/train.npz',ROOT/'data/gmaw/train.npz',ROOT/'data/resistance_spot_welding/train.npz',ROOT/'data/tig_welding/train.npz',ROOT/'data/fdm/train.csv')
def prepare():
    if all(x.is_file() for x in EXPECTED):
        return False
    if not ARCHIVE.is_file():
        raise FileNotFoundError('training_data.zip is missing.')
    with zipfile.ZipFile(ARCHIVE) as archive:
        bad=archive.testzip()
        if bad:raise RuntimeError(f'Training archive damaged: {bad}')
        for item in archive.infolist():
            dest=(ROOT/item.filename).resolve()
            if not dest.is_relative_to(ROOT.resolve()):raise RuntimeError('Unsafe path in training archive')
        archive.extractall(ROOT)
    if not all(x.is_file() for x in EXPECTED):
        raise RuntimeError('The training archive is incomplete.')
    print('Synthetic data extracted into data/.')
    return True
if __name__=='__main__':prepare()
