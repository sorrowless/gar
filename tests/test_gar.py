import builtins
import io
import pytest
from hamcrest import *
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
    def shortOpts(self):
        return " 235550"

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

    @pytest.fixture
    def configMock(self, configfile):
        file_spec = [ '__enter__', '__exit__' ]
        m = MagicMock(spec=file_spec)
        handle = MagicMock(spec=file_spec)
        handle.__enter__.return_value = configfile
        m.return_value = handle
        return m

    def test_without_arguments(self):
        with pytest.raises(docopt.DocoptExit):
            o = Options()

    def test_with_change_id(self):
        sys.argv = '101010'
        o = Options()
        assert_that(o, is_not({}))

    def test_options_key(self, opts):
        sys.argv = opts
        o = Options()
        assert_that(o.args.get("--key"), equal_to('/root/test'))

    def test_options_keypass(self, opts):
        sys.argv = opts
        o = Options()
        assert_that(o.args.get("--keypass"), equal_to('testPassword'))

    def test_options_host(self, opts):
        sys.argv = opts
        o = Options()
        assert_that(o.args.get("--host"), equal_to('review.localhost'))

    def test_options_port(self, opts):
        sys.argv = opts
        o = Options()
        assert_that(o.args.get("--port"), equal_to('44544'))

    def test_options_user(self, opts):
        sys.argv = opts
        o = Options()
        assert_that(o.args.get("--user"), equal_to('testUser'))

    def test_options_project(self, opts):
        sys.argv = opts
        o = Options()
        assert_that(o.args.get("--project"), equal_to('newProject'))

    def test_options_addresses(self, opts):
        sys.argv = opts
        o = Options()
        assert_that(o.args.get("--addresses"), equal_to('/root/reviewers'))

    def test_options_verbosity(self, opts):
        for i in range(1,6):
            newopts = opts + ' -' + 'v'*i
            sys.argv = newopts
            o = Options()
            assert_that(o.args.get("-v"), equal_to(i))

    def test_options_configfile(self, opts, configMock):
        sys.argv = opts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile, is_not(equal_to({})))

    def test_options_configfile_overrides_key(self, shortOpts, configMock):
        sys.argv = shortOpts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile.get("--key"), equal_to("/root/newkey"))
        assert_that(o.options.get("--key"), equal_to("/root/newkey"))

    def test_options_configfile_overrides_keypass(self, shortOpts, configMock):
        sys.argv = shortOpts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile.get("--keypass"), equal_to("newPassword"))
        assert_that(o.options.get("--keypass"), equal_to("newPassword"))

    def test_options_configfile_overrides_host(self, shortOpts, configMock):
        sys.argv = shortOpts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile.get("--host"), equal_to("newhost.localhost"))
        assert_that(o.options.get("--host"), equal_to("newhost.localhost"))

    def test_options_configfile_overrides_port(self, shortOpts, configMock):
        sys.argv = shortOpts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile.get("--port"), equal_to("44744"))
        assert_that(o.options.get("--port"), equal_to("44744"))

    def test_options_configfile_overrides_user(self, shortOpts, configMock):
        sys.argv = shortOpts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile.get("--user"), equal_to("newUser"))
        assert_that(o.options.get("--user"), equal_to("newUser"))

    def test_options_configfile_overrides_project(self, shortOpts, configMock):
        sys.argv = shortOpts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile.get("--project"), equal_to("projectTwo"))
        assert_that(o.options.get("--project"), equal_to("projectTwo"))

    def test_options_configfile_overrides_addresses(self, shortOpts, configMock):
        sys.argv = shortOpts
        with patch('builtins.open', configMock):
            o = Options()
        assert_that(o.conffile.get("--addresses"), equal_to("/root/newReviewers"))
        assert_that(o.options.get("--addresses"), equal_to("/root/newReviewers"))


class TestGar:
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

    def test_readPrivateKeyPassword(self, opts):
        sys.argv = opts
        o = Options()
        c = Gar(o.options, o.logger)
        c.readPrivateKeyPassword()
        assert_that(c.pkeypassword, equal_to(o.options.get("--keypass")))

