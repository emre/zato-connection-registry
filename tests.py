import copy
import json
import tempfile
import unittest

import responses

from zato_connection_registry.registry import Registry

SINGLE_CHANNEL_DATA = {
    'sec_tls_ca_cert_id': None,
    'sec_type': None,
    'cache_type': None,
    'service_name': 'account-service.account-sync-service',
    'is_internal': False,
    'soap_action': '',
    'has_rbac': False,
    'serialization_type': 'string',
    'ping_method': 'HEAD',
    'id': 660,
    'transport': 'plain_http',
    'soap_version': None,
    'security_name': None,
    'content_encoding': '',
    'cache_expiry': 0,
    'method': '',
    'is_active': True,
    'host': None,
    'content_type': None,
    'security_id': None,
    'url_path': '/test/v1/accounts/sync',
    'merge_url_params_req': True,
    'name': '/test/v1/accounts/sync',
    'sec_use_rbac': False,
    'data_format': 'json',
    'cache_id': None,
    'pool_size': 20,
    'url_params_pri': 'qs-over-path',
    'connection': 'channel',
    'timeout': 10,
    'service_id': 581,
    'params_pri': 'channel-params-over-msg',
    'cache_name': None
}

SERVICE_LIST_MOCK_DATA = {
    'zato_env': {
        'cid': '36972648978ec860883886b1',
        'details': '',
        'result': 'ZATO_OK'
    }, 'zato_http_soap_get_list_response': [SINGLE_CHANNEL_DATA, ]
}


class TestRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = Registry(
            "http://localhost:11223",
            "pubapi",
            "123",
        )

    @responses.activate
    def test_load_rest_channels(self):
        responses.add(
            responses.POST,
            'http://localhost:11223/zato/json/zato.http-soap.get-list',
            json=SERVICE_LIST_MOCK_DATA, status=200
        )

        self.registry.load_rest_channels()

        self.assertEqual(len(self.registry.rest_channels), 1)
        self.assertEqual(
            self.registry.rest_channels[0]["name"],
            "/test/v1/accounts/sync",
        )

    @responses.activate
    def test_dump_to_json(self):
        responses.add(
            responses.POST,
            'http://localhost:11223/zato/json/zato.http-soap.get-list',
            json=SERVICE_LIST_MOCK_DATA, status=200
        )
        with tempfile.NamedTemporaryFile(
                suffix='.json') as tf:
            self.registry.dump_to_json(tf.name)
            backup_data = json.load(tf)

            self.assertEqual(len(backup_data), 1)
            self.assertEqual(
                backup_data[0]["name"],
                "/test/v1/accounts/sync",
            )

    def test_channel_to_request_params(self):
        params = self.registry.channel_to_request_params(SINGLE_CHANNEL_DATA)

        self.assertEqual(params["connection"], "channel")
        SINGLE_CHANNEL_DATA_AS_OUTGOING = copy.copy(SINGLE_CHANNEL_DATA)
        SINGLE_CHANNEL_DATA_AS_OUTGOING.update({"connection": "foo"})
        params = self.registry.channel_to_request_params(
            SINGLE_CHANNEL_DATA_AS_OUTGOING)
        self.assertEqual(params["connection"], "outgoing")


if __name__ == '__main__':
    unittest.main()
