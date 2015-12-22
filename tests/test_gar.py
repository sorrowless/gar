import builtins
import io
import pytest
import docopt
import sys
from gar.gar import Options, Gar
from unittest.mock import patch, Mock, MagicMock, mock_open


class TestOptions:
    @pytest.fixture
    def opts(self):
        key = '/root/test'
        keypass = 'testPassword'
        host = 'review.localhost'
        port = '44544'
        user = 'testUser'
        project = 'newProject'
        addresses = '/root/reviewers'
        return " --key {} \
                --keypass {} \
                --host {} \
                --port {} \
                --user {} \
                --project {} \
                --addresses {} 235550".format(key, keypass, host, port, user,
                        project, addresses)

    @pytest.fixture
    def configfile(self):
        data = """{
            "--key": "/root/newkey",
            "--keypass": "newPassword",
            "--host": "newhost.localhost",
            "--port": "44744",
            "--user": "newUser",
            "--project": "projectTwo",
            "--addresses": "/root/newReviewers"
        }
        """
        return data

    def test_without_arguments(self):
        with pytest.raises(docopt.DocoptExit):
            o = Options()

    def test_with_change_id(self):
        sys.argv = '101010'
        o = Options()
        assert o

    def test_options_key(self, opts):
        sys.argv = opts
        o = Options()
        assert o.args.get("--key") == '/root/test'

    def test_options_keypass(self, opts):
        sys.argv = opts
        o = Options()
        assert o.args.get("--keypass") == 'testPassword'

    def test_options_host(self, opts):
        sys.argv = opts
        o = Options()
        assert o.args.get("--host") == 'review.localhost'

    def test_options_port(self, opts):
        sys.argv = opts
        o = Options()
        assert o.args.get("--port") == '44544'

    def test_options_user(self, opts):
        sys.argv = opts
        o = Options()
        assert o.args.get("--user") == 'testUser'

    def test_options_project(self, opts):
        sys.argv = opts
        o = Options()
        assert o.args.get("--project") == 'newProject'

    def test_options_addresses(self, opts):
        sys.argv = opts
        o = Options()
        assert o.args.get("--addresses") == '/root/reviewers'

    def test_options_verbosity(self, opts):
        for i in range(1,6):
            newopts = opts + ' -' + 'v'*i
            sys.argv = newopts
            o = Options()
            assert o.args.get("-v") == i

    def test_options_configfile(self, opts, configfile):
        sys.argv = opts

        file_spec = [ '__enter__', '__exit__' ]
        m = MagicMock(spec=file_spec)
        handle = MagicMock(spec=file_spec)
        handle.__enter__.return_value = configfile
        m.return_value = handle

        with patch('builtins.open', m):
            o = Options()
        assert o.conffile != {}

