import pathlib
import sys

# Make scripts/ importable without installing
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
