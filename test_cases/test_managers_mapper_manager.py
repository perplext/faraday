'''
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

'''
from functools import partial

import pytest

from managers.mapper_manager import MapperManager
from persistence.server.server import _create_server_api_url
from persistence.server.models import (
    Host,
    Service,
    Vuln,
    Credential,
    VulnWeb,
    Note,
    Command,
)
import persistence.server.server
from persistence.server.utils import (
    get_host_properties,
    get_service_properties,
    get_vuln_properties,
    get_vuln_web_properties,
    get_credential_properties, get_command_properties)
from test_cases.factories import (
    WorkspaceFactory,
    CommandFactory,
    HostFactory,
    ServiceFactory,
    VulnerabilityFactory,
    CredentialFactory,
    VulnerabilityWebFactory,
    CommentFactory,
    EmptyCommandFactory)

# OBJ_DATA is used to parametrize tests (https://docs.pytest.org/en/latest/parametrize.html)
# We use it to test all model classes.
# to add more tests you need to add items in the list or more objects in the dict.

OBJ_DATA = {
    # the key is the object being tested
    Host: [{
        'factory': HostFactory,
        # api_end_point is used to assert the generated url.
        'api_end_point': 'hosts',
        # parent is used to assert parent information is correcly generated.
        'parent': {},
        # data is used to instanciate a persistence.server.models class.
        'data': {
            '_id': 1,
            'name': '192.168.0.20',
            'description': 'My computer',
            'default_gateway': '192.168.0.1',
            'hostnames': [],
            'os': 'Debian',
            'owned': False,
            'owner': 'leo'
        },
        # expected_payload is asserted with the generated payload that will be sent to the API of faraday-server
        'expected_payload': {
                'command_id': None,
                'default_gateway': '192.168.0.1',
                'description': 'My computer',
                'ip': '192.168.0.20',
                'hostnames': [],
                'os': 'Debian',
                'owned': False,
                'owner': 'leo',
                'parent': None,
                'type': 'Host'
        },
    }],
    Service: [{
        'factory': ServiceFactory,
        'api_end_point': 'services',
        'parent': {
            'parent_type': 'Host',
            'parent_factory': HostFactory
        },
        'data': {
            '_id': 1,
            'name': 'Service port 60',
            'description': 'My service',
            'owned': False,
            'owner': 'leo',
            'protocol': 'tcp',
            'ports': 60,
            'version': '2',
            'status': 'open',
            'vulns': 0,
        },
        'expected_payload': {
            'command_id': None,
            'name': 'Service port 60',
            'description': 'My service',
            'protocol': 'tcp',
            'ports': [60],
            'version': '2',
            'status': 'open',
            'owned': False,
            'owner': 'leo',
            'type': 'Service'
        },
    }],
    Vuln: [{
        'factory': VulnerabilityFactory,
        'api_end_point': 'vulns',
        'parent': {
            'parent_type': 'Service',
            'parent_factory': ServiceFactory
        },
        'data': {
            '_id': 1,
            'name': 'Service vulnerable',
            'desc': 'My vuln',
            'owned': False,
            'owner': 'leo',
            'severity': 'critical',
            'data': '',
        },
        'expected_payload': {
            'command_id': None,
            'name': 'Service vulnerable',
            'desc': 'My vuln',
            'description': 'My vuln',
            'owner': 'leo',
            'owned': False,
            'confirmed': False,
            'severity': 'critical',
            'data': '',
            'type': 'Vulnerability',
            'parent_type': 'Service',
            'policyviolations': [],
            'refs': [],
            'status': 'opened',
            'resolution': None,
        },
    }],
    VulnWeb: [{
        'factory': VulnerabilityWebFactory,
        'api_end_point': 'vulns',
        'parent': {
            'parent_type': 'Service',
            'parent_factory': ServiceFactory
        },
        'data': {
            '_id': 1,
            'name': 'Service vulnerable',
            'desc': 'My vuln',
            'owned': False,
            'owner': 'leo',
            'severity': 'critical',
            'data': '',
            'website': 'www.faradaysec.com',
            'method': 'GET',
            'pname': 'param_name',
            'params': 'params',
            'path': 'path',
            'request': 'test',
            'query': 'query test',
            'response': 'repsonse data',
        },
        'expected_payload': {
            'category': '',
            'command_id': None,
            'name': 'Service vulnerable',
            'desc': 'My vuln',
            'description': 'My vuln',
            'owner': 'leo',
            'owned': False,
            'confirmed': False,
            'severity': 'critical',
            'data': '',
            'type': 'VulnerabilityWeb',
            'parent_type': 'Service',
            'policyviolations': [],
            'refs': [],
            'status': 'opened',
            'resolution': None,
            'website': 'www.faradaysec.com',
            'method': 'GET',
            'pname': 'param_name',
            'params': 'params',
            'path': 'path',
            'request': 'test',
            'query': 'query test',
            'response': 'repsonse data',
        },
    }],
    Credential: [{
        'factory': CredentialFactory,
        'api_end_point': 'credential',
        'parent': {
            'parent_type': 'Host',
            'parent_factory': HostFactory
        },
        'data': {
            '_id': 1,
            'name': 'New credential',
            'description': 'Test credential',
            'owned': False,
            'owner': 'leo',
            'password': 'testpass',
            'username': 'username1'
        },
        'expected_payload': {
            'command_id': None,
            'name': 'New credential',
            'description': 'Test credential',
            'owner': 'leo',
            'owned': False,
            'password': 'testpass',
            'username': 'username1',
            'type': 'Cred',
        },
    }],
    Note: [{
        'factory': CommentFactory,
        'api_end_point': 'comment',
        # parent not used
        'parent': {
            'parent_type': 'Host',
            'parent_factory': HostFactory
        },
        'data': {
            '_id': 1,
            'text': 'Text from Note',
            'object_id': 10,
            'object_type': 'Host',
            'owned': False,
            'owner': 'leo',
            'password': 'testpass',
            'username': 'username1'
        },
        'expected_payload': {
            'command_id': None,
            'description': '',
            'name': None,
            'object_id': 10,
            'object_type': 'Host',
            'owned': False,
            'owner': 'leo',
            'text': 'Text from Note',
            'type': 'Note'},
    }],
    Command: [{
        'factory': EmptyCommandFactory,
        'api_end_point': 'commands',
        # parent not used
        'parent': {
            'parent_type': 'Host',
            'parent_factory': HostFactory
        },
        'data': {
            'itime': 1513959206,
            'ip': "192.168.124.1",
            'hostname': "mandarina",
            'command': "Import Nexpose:",
            'tool': "Import Nexpose:",
            'import_source': "report",
            'user': "leonardo",
            'workspace': "airbnb",
            'duration': 0.164561,
            'params': "/home/lcubo/.faraday/report/airbnb/nexpose_5.7.19_Website_PT.xml",
            '_id': 280
        },
        'expected_payload':{
            'command': 'Import Nexpose:',
            'tool': "Import Nexpose:",
            'import_source': "report",
            'duration': 0.164561,
            'hostname': 'mandarina',
            'ip': '192.168.124.1',
            'itime': 1513959206,
            'params': '/home/lcubo/.faraday/report/airbnb/nexpose_5.7.19_Website_PT.xml',
            'type': 'CommandRunInformation',
            'user': 'leonardo',
            'workspace': u'test'
        }
    }]
}


# the following dict is used to parametrize find (GET) tests
# mocked_response is the json returned by the api
# serialized_expected_results the expected serialized result.
GET_OBJ_DATA = {
    VulnWeb: [
        {
            'factory': VulnerabilityWebFactory,
            'api_end_point': 'vulns',
            'get_properties_function': get_vuln_web_properties,
            'mocked_response': {
                "website": "www.faradaysec.com",
                "_rev": "",
                "parent_type": "Service",
                "owned": False,
                "owner": "leonardo",
                "query": "query",
                "refs": [
                "ref"
                ],
                "impact": {
                    "accountability": False,
                    "integrity": False,
                    "confidentiality": False,
                    "availability": False
                },
                "confirmed": True,
                "severity": "high",
                "service": {
                    "status": "open",
                    "protocol": "fdsf",
                    "name": "gfdgfd",
                    "summary": "(32/fdsf) gfdgfd",
                    "version": "",
                    "_id": 299,
                    "ports": "32"
                },
                "policyviolations": [],
                "params": "parameters",
                "type": "VulnerabilityWeb",
                "method": "GET",
                "metadata": {
                "update_time": 1513982385000,
                "update_user": "",
                "update_action": 0,
                "creator": "",
                "create_time": 1513982385000,
                "update_controller_action": "",
                "owner": "leonardo",
                "command_id": None
                },
                "status": "opened",
                "issuetracker": {},
                "description": "Description",
                "parent": 299,
                "tags": [ ],
                "easeofresolution": "simple",
                "hostnames": [
                "macbookpro-c9a7"
                ],
                "pname": "pname",
                "date": "2017-12-22T19:39:45.014203+00:00",
                "path": "path",
                "data": "data",
                "response": "response",
                "desc": "Description",
                "name": "Vuln web",
                "obj_id": "348",
                "request": "request",
                "_attachments": [],
                "target": "172.16.138.1",
                "_id": 348,
                "resolution": "resolution"
                },
            'serialized_expected_results': {
                'confirmed': True,
                'data': 'data',
                'desc': 'Description',
                'description': 'Description',
                'name': 'Vuln web',
                'owned': False,
                'owner': 'leonardo',
                'parent': 299,
                'parent_type': 'Service',
                'params': 'parameters',
                'path': 'path',
                'policyviolations': [],
                'response': 'response',
                'method': 'GET',
                'refs': ['ref'],
                'request': 'request',
                'resolution': 'resolution',
                'severity': 'high',
                'status': 'opened',
                'website': 'www.faradaysec.com',
                "query": "query",
                "pname": "pname"
            }

        }
    ],
    Vuln: [
        {
            'factory': VulnerabilityFactory,
            'api_end_point': 'vulns',
            'get_properties_function': get_vuln_properties,
            'mocked_response': {
                "website": "",
                "_rev": "",
                "parent_type": "Service",
                "owned": False,
                "owner": "leonardo",
                "query": "",
                "refs": [],
                "impact": {
                    "accountability": False,
                    "integrity": False,
                    "confidentiality": False,
                    "availability": False
                },
                "confirmed": True,
                "severity": "med",
                "service": {
                    "status": "open",
                    "protocol": "tcp",
                    "name": "ssh",
                    "summary": "(21/tcp) ssh",
                    "version": "",
                    "_id": 1,
                    "ports": "21"
                },
                "policyviolations": [],
                "params": "",
                "type": "Vulnerability",
                "method": "",
                "metadata": {
                    "update_time": 1513290499000,
                    "update_user": "",
                    "update_action": 0,
                    "creator": "",
                    "create_time": 1513290499000,
                    "update_controller_action": "",
                    "owner": "leonardo",
                    "command_id": None
                },
                "status": "opened",
                "issuetracker": {},
                "description": "description",
                "parent": 1,
                "tags": [],
                "easeofresolution": "trivial",
                "hostnames": [],
                "pname": "",
                "date": "2017-12-14T19:28:19.427274+00:00",
                "path": "",
                "data": "data",
                "response": "",
                "desc": "description",
                "name": "Vuln test",
                "obj_id": "1",
                "request": "",
                "_attachments": [],
                "target": "192.168.0.1",
                "_id": 1,
                "resolution": ""
        },
            'serialized_expected_results': {
                'confirmed': True,
                'data': 'data',
                'desc': 'description',
                'description': 'description',
                'name': 'Vuln test',
                'owned': False,
                'owner': 'leonardo',
                'parent': 1,
                'parent_type': 'Service',
                'policyviolations': [],
                'refs': [],
                'resolution': '',
                'severity': 'med',
                'status': 'opened'
            }

        }
    ],
    Host: [
        {
            'factory': HostFactory,
            'api_end_point': 'hosts',
            'get_properties_function': get_host_properties,
            'mocked_response': {
                    'name': "192.168.1.1", 'default_gateway': None,
                    'ip': "192.168.1.1", '_rev': "",
                    'description': "Test description", 'owned': False,
                    'services': 7, 'hostnames': [],
                    'vulns': 45, 'owner': "leonardo",
                    'credentials': 1, '_id': 16,
                    'os': "Linux 2.6.9", 'id': 16,
                    'metadata': {
                        'update_time': 1513381792000, 'update_user': "",
                        'update_action': 0, 'creator': "",
                        'create_time': 1513381792000, 'update_controller_action': "",
                        'owner': "leonardo", 'command_id': None
                    }
            },
            'serialized_expected_results': {
                'description': 'Test description',
                'ip': '192.168.1.1',
                'os': 'Linux 2.6.9',
                'hostnames': [],
                'owned': False,
                'owner': 'leonardo'}

        }
    ],
    Service: [
        {
            'factory': ServiceFactory,
            'api_end_point': 'services',
            'parent': {
                'parent_type': 'Host',
                'parent_factory': HostFactory
            },
            'get_properties_function': get_service_properties,
            'mocked_response': {
                "status": "open",
                "protocol": "tcp",
                "description": "Test description",
                "vulns": 2,
                "_rev": "",
                "metadata": {
                    "update_time": 1513290473000,
                    "update_user": "",
                    "update_action": 0,
                    "creator": "",
                    "create_time": 1513290473000,
                    "update_controller_action": "",
                    "owner": "leonardo",
                    "command_id": None
                },
                "owned": False,
                "summary": "(21/tcp) ssh",
                "port": 21,
                "owner": "leonardo",
                "version": "",
                "host_id": 1,
                "parent": 1,
                "id": 1,
                "credentials": 0,
                "_id": 1,
                "ports": 21,
                "name": "ssh"
            },
            'serialized_expected_results': {
                'name': 'ssh',
                'description': 'Test description',
                'ports': [21],
                'protocol': 'tcp',
                'status': 'open',
                'parent': 1,
                'version': '',
                'owned': False,
                'owner': 'leonardo'
            }

        }
    ],
    Credential: [{
        'factory': ServiceFactory,
        'api_end_point': 'credential',
        'parent': {
            'parent_type': 'Host',
            'parent_factory': HostFactory
        },
        'get_properties_function': get_credential_properties,
        'mocked_response': {
            "username": "user1",
            "password": "secretpassword",
            "description": "Credential obtained using hashcat",
            "couchdbid": "",
            'parent': 64,
            'parent_type': 'Host',
            "_rev": "",
            "metadata": {
                "update_time": 1514312337000,
                "update_user": "",
                "update_action": 0,
                "creator": "",
                "create_time": 1514312336000,
                "update_controller_action": "",
                "owner": "leonardo",
                "command_id": None
            },
            "owned": False,
            "owner": "leonardo",
            "_id": 2,
            "id": 2,
            "name": "dsds"
            },
        'serialized_expected_results': {
            'description': 'Credential obtained using hashcat',
            'name': 'dsds',
            'owned': False,
            'owner': 'leonardo',
            'parent': 64,
            'parent_type': 'Host',
            'password': 'secretpassword',
            'username': 'user1'
        }
    }],
    Credential: [{
        'factory': ServiceFactory,
        'api_end_point': 'credential',
        'parent': {
            'parent_type': 'Host',
            'parent_factory': HostFactory
        },
        'get_properties_function': get_credential_properties,
        'mocked_response': {
            "username": "user1",
            "password": "secretpassword",
            "description": "Credential obtained using hashcat",
            "couchdbid": "",
            'parent': 64,
            'parent_type': 'Host',
            "_rev": "",
            "metadata": {
                "update_time": 1514312337000,
                "update_user": "",
                "update_action": 0,
                "creator": "",
                "create_time": 1514312336000,
                "update_controller_action": "",
                "owner": "leonardo",
                "command_id": None
            },
            "owned": False,
            "owner": "leonardo",
            "_id": 2,
            "id": 2,
            "name": "dsds"
        },
        'serialized_expected_results': {
            'description': 'Credential obtained using hashcat',
            'name': 'dsds',
            'owned': False,
            'owner': 'leonardo',
            'parent': 64,
            'parent_type': 'Host',
            'password': 'secretpassword',
            'username': 'user1'
        }
    }],
    Command: [{
        'factory': ServiceFactory,
        'api_end_point': 'commands',
        'parent': {
            'parent_type': 'Host',
            'parent_factory': HostFactory
        },
        'get_properties_function': get_command_properties,
        'mocked_response': {
            "itime": 1513365824,
            "ip": "192.168.20.53",
            "hostname": "mandarina",
            "command": "Import Nessus:",
            "tool": "Import Nessus:",
            "import_source": "report",
            "user": "lcubo",
            "workspace": "dsadsa",
            "duration": "In progress",
            "params": "/home/lcubo/.faraday/report/dsadsa/nessus_report_Remote.nessus",
            "_id": 1
        },
        'serialized_expected_results': {
            'command': 'Import Nessus:',
            "tool": "Import Nessus:",
            'duration': 'In progress',
            "import_source": "report",
            'hostname': 'mandarina',
            'ip': '192.168.20.53',
            'itime': 1513365824,
            'params': '/home/lcubo/.faraday/report/dsadsa/nessus_report_Remote.nessus',
            'user': 'lcubo'}
    }]
}

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.mark.usefixtures('logged_user')
class TestMapperManager():

    @pytest.mark.parametrize("obj_class, many_test_data", OBJ_DATA.items())
    def test_save_without_command(self, obj_class, many_test_data, monkeypatch, session):
        """
            This test verifies that the request made to the api are the expected ones
        """
        workspace = WorkspaceFactory.create(name='test')
        session.commit()
        mapper_manager = MapperManager()
        mapper_manager.createMappers(workspace.name)

        for test_data in many_test_data:
            raw_data = test_data['data']
            if test_data['parent']:
                parent = test_data['parent']['parent_factory'].create()
                session.commit()
                test_data['data']['parent'] = parent.id
                test_data['data']['parent_type'] = test_data['parent']['parent_type']
                if obj_class not in [Note, Command]:
                    test_data['expected_payload']['parent'] = parent.id
                if obj_class in [Vuln, Credential]:
                    test_data['expected_payload']['parent_type'] = test_data['parent']['parent_type']
            def mock_server_post(test_data, post_url, update=False, expected_response=201, **params):
                assert post_url == '{0}/ws/test/{1}/'.format(
                    _create_server_api_url(), test_data['api_end_point'])
                assert expected_response == 201
                assert update == False
                if obj_class not in [Command]:
                    metadata = params.pop('metadata')
                    assert metadata['owner'] == test_data['expected_payload']['owner']
                assert params == test_data['expected_payload']
                return {
                    'id': 1,
                    'ok': True,
                    'rev': ''
                }

            monkeypatch.setattr(persistence.server.server, '_post', partial(mock_server_post, test_data))
            obj = obj_class(raw_data, workspace.name)
            mapper_manager.save(obj)

    @pytest.mark.parametrize("obj_class, many_test_data", OBJ_DATA.items())
    def test_save_with_command(self, obj_class, many_test_data, monkeypatch, session):
        if obj_class == Command:
            return
        workspace = WorkspaceFactory.create(name='test')
        command = CommandFactory.create(workspace=workspace)
        session.commit()
        mapper_manager = MapperManager()
        mapper_manager.createMappers(workspace.name)
        for test_data in many_test_data:
            raw_data = test_data['data']
            if test_data['parent']:
                parent = test_data['parent']['parent_factory'].create()
                session.commit()

                test_data['data']['parent'] = parent.id
                test_data['data']['parent_type'] = test_data['parent']['parent_type']
                if obj_class not in [Note]:
                    test_data['expected_payload']['parent'] = parent.id
                if obj_class in [Vuln, Credential]:
                    test_data['expected_payload']['parent_type'] = test_data['parent']['parent_type']
            def mock_server_post(test_data, post_url, update=False, expected_response=201, **params):
                assert post_url == '{0}/ws/test/{1}/?command_id={2}'.format(_create_server_api_url(), test_data['api_end_point'], params['command_id'])
                assert expected_response == 201
                assert update == False
                metadata = params.pop('metadata')
                assert metadata['owner'] == test_data['expected_payload']['owner']
                params.pop('command_id')
                test_data['expected_payload'].pop('command_id')
                assert params == test_data['expected_payload']
                return {
                    'id': 1,
                    'ok': True,
                    'rev': ''
                }

            monkeypatch.setattr(persistence.server.server, '_post', partial(mock_server_post, test_data))
            obj = obj_class(raw_data, workspace.name)
            mapper_manager.save(obj, command.id)

    @pytest.mark.parametrize("obj_class, many_test_data", OBJ_DATA.items())
    def test_update_without_command(self, obj_class, many_test_data, monkeypatch, session):
        workspace = WorkspaceFactory.create(name='test')
        mapper_manager = MapperManager()
        mapper_manager.createMappers(workspace.name)

        for test_data in many_test_data:
            relational_model = test_data['factory'].create()
            session.add(relational_model)
            session.commit()
            raw_data = test_data['data']
            if test_data['parent']:
                parent = test_data['parent']['parent_factory'].create()
                session.add(parent)
                session.commit()

                test_data['data']['parent'] = parent.id
                test_data['data']['parent_type'] = test_data['parent']['parent_type']
                if obj_class not in [Note, Command]:
                    test_data['expected_payload']['parent'] = parent.id
                if obj_class in [Vuln, Credential]:
                    test_data['expected_payload']['parent_type'] = test_data['parent']['parent_type']
            def mock_server_put(test_data, put_url, update=False, expected_response=201, **params):
                assert put_url == '{0}/ws/test/{1}/{2}/'.format(_create_server_api_url(), test_data['api_end_point'], test_data['id'])
                assert expected_response == 200
                assert update == False
                if obj_class not in [Command]:
                    metadata = params.pop('metadata')
                    assert metadata['owner'] == test_data['expected_payload']['owner']
                params.pop('command_id', None)
                test_data['expected_payload'].pop('command_id', None)
                assert params == test_data['expected_payload']

                return {
                    'id': 1,
                    'ok': True,
                    'rev': ''
                }

            raw_data['id'] = relational_model.id
            test_data['id'] = relational_model.id
            monkeypatch.setattr(persistence.server.server, '_put', partial(mock_server_put, test_data))

            obj = obj_class(raw_data, workspace.name)
            mapper_manager.update(obj)

    @pytest.mark.parametrize("obj_class, many_test_data", OBJ_DATA.items())
    def test_update_with_command(self, obj_class, many_test_data, monkeypatch, session):
        if obj_class in [Command]:
            return
        workspace = WorkspaceFactory.create(name='test')
        command = CommandFactory.create(workspace=workspace)
        session.add(command)
        session.commit()
        mapper_manager = MapperManager()
        mapper_manager.createMappers(workspace.name)

        for test_data in many_test_data:
            raw_data = test_data['data']
            if test_data['parent']:
                parent = test_data['parent']['parent_factory'].create()
                session.add(parent)
                session.commit()
                test_data['data']['parent'] = parent.id
                test_data['data']['parent_type'] = test_data['parent']['parent_type']
                test_data['expected_payload']['parent'] = parent.id
                if obj_class in [Vuln, Credential]:
                    test_data['expected_payload']['parent_type'] = test_data['parent']['parent_type']
            relational_model = test_data['factory'].create()
            session.add(relational_model)
            session.commit()
            def mock_server_put(put_url, update=False, expected_response=201, **params):
                assert put_url == '{0}/ws/test/{1}/{2}/?command_id={3}'.format(
                    _create_server_api_url(),
                    test_data['api_end_point'],
                    test_data['id'],
                    params['command_id'])
                assert expected_response == 200
                assert update == False
                return {
                    'id': 1,
                    'ok': True,
                    'rev': ''
                }

            raw_data['id'] = relational_model.id
            test_data['id'] = relational_model.id
            monkeypatch.setattr(persistence.server.server, '_put', mock_server_put)
            obj = obj_class(raw_data, workspace.name)
            mapper_manager.update(obj, command.id)

    @pytest.mark.parametrize("obj_class, many_test_data", GET_OBJ_DATA.items())
    def test_find_obj_by_id(self, obj_class, many_test_data, session, monkeypatch):
        for test_data in many_test_data:
            persisted_obj = test_data['factory'].create()
            session.add(persisted_obj)
            session.commit()
            mapper_manager = MapperManager()
            mapper_manager.createMappers(persisted_obj.workspace.name)

            def mock_unsafe_io_with_server(host, test_data, server_io_function, server_expected_response, server_url, **payload):
                mocked_response = test_data['mocked_response']
                assert '{0}/ws/{1}/{2}/{3}/'.format(
                    _create_server_api_url(),
                    persisted_obj.workspace.name,
                    test_data['api_end_point'],
                    persisted_obj.id) == server_url
                return MockResponse(mocked_response, 200)

            monkeypatch.setattr(persistence.server.server, '_unsafe_io_with_server', partial(mock_unsafe_io_with_server, persisted_obj, test_data))
            found_obj = mapper_manager.find(obj_class.class_signature, persisted_obj.id)
            serialized_obj = test_data['get_properties_function'](found_obj)
            if obj_class not in [Command]:
                metadata = serialized_obj.pop('metadata')
            assert serialized_obj == test_data['serialized_expected_results']