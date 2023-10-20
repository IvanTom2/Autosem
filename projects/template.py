import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "autosem"))
sys.path.append(str(Path(__file__).parent.parent))

from autosem.word_extraction import *
from autosem.measures_extraction import *
from autosem.counts_extraction import *
from autosem.cross_semantic import *
from util import save, upload, concat_rx


if __name__ == "__main__":
    """
    Import this template for your projects.
    """

    # use it for lanuage setup
    eng = LanguageRules(
        "english",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
        symbols="",
    )
