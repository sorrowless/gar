import pytest
import docopt
import sys
from gar.gar import Options, Gar

class TestOptions:
    def test_without_arguments(self):
        with pytest.raises(docopt.DocoptExit):
            o = Options()

    def test_with_change_id(self):
        sys.argv = '101010'
        o = Options()
        assert o

    def test_version(self):
        sys.argv = ' --version'
        try:
            o = Options()
        except:
            pass
        assert o.args.get('--version') == True


