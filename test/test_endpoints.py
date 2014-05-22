from app import app


class TestEndpoints(object):
    """Tests for HTTP Endpoints"""
    @classmethod
    def setup_class(cls):
        cls.app = app.test_client()

    @classmethod
    def teardown_class(cls):
        pass

    def test_index(self):
        rv = self.app.get('/')
        assert "Futurama" in rv.data

    def test_mozilla_inbound(self):
        rv = self.app.get('/?tree=mozilla-inbound')
        assert "Futurama" in rv.data

    def test_mozilla_central(self):
        rv = self.app.get('/?tree=mozilla-central')
        assert "Futurama" in rv.data

    def test_fx_team(self):
        rv = self.app.get('/?tree=fx-team')
        assert "Futurama" in rv.data