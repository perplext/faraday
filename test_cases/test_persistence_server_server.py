'''
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

'''
import os

import responses
import requests

import pytest

from persistence.server import server


@pytest.mark.usefixtures('logged_user')
class TestServerFuncions:

    @responses.activate
    def test_test_server_url_server_runnimg(self, test_client):
        """
            The name of the method is correct we are testing the function:
            check_server_url

        """
        mocked_response = {
            "Faraday Server": "Running",
            "Version":"2.7.1"
        }

        responses.add(responses.GET, 'http://localhost/_api/v2/info',
                      json=mocked_response, status=200)
        assert server.check_server_url('http://localhost')

    @responses.activate
    def test_test_server_url_another_http_returns_404(self):
        responses.add(responses.GET, 'http://localhost/_api/v2/info',
                      status=404)
        assert not server.check_server_url('http://localhost')

    def test_test_server_url_aserver_down(self, test_client):
        assert not server.check_server_url('http://localhost')
