import pytest
import docopt
from gar.gar import Options, Gar

def test_Options():
    with pytest.raises(docopt.DocoptExit):
        o = Options()
