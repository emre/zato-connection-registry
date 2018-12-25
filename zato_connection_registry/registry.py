import json
import logging

from zato.client import APIClient

logger = logging.getLogger(__name__)


class Registry:
    """
    A Registry class to fetch and push incoming/outgoing connection
    definitions from any Zato instance, to any Zato instance.
    """

    def __init__(self, zato_addr, username, password,
                 path="/zato/json/{}", cluster_id=None):
        """
        Note: The default path argument works for Zato 3.0. You may need to
        change if you use older Zato versions.

        Args:
            :param zato_addr (str): The address of Zato instance
            :param username (str): Username for the Zato client
            :param password (str): Password for the Zato client
            :param path (str): URL path for the API calls.
            :param cluster_id (int): The cluster id to pull/push connections
        """
        self.zato_addr = zato_addr
        self.username = username
        self.password = password
        self.path = path
        self.client = APIClient(
            zato_addr,
            self.username,
            self.password,
            path=path
        )
        self.cluster_id = cluster_id or 1
        self.rest_channels = []

    def load_rest_channels(self):
        """Loads all REST connection definitions from the remote Zato server
        and injects it to self.rest_channels property.
        """
        response = self.client.invoke(
            "zato.http-soap.get-list",
            {"cluster_id": self.cluster_id}
        )

        response_key = "zato_http_soap_get_list_response"
        for outgoing_connection in response.data[response_key]:

            # skip internal connections
            if outgoing_connection.get("is_internal"):
                continue

            self.rest_channels.append(outgoing_connection)

    def dump_to_json(self, json_file):
        """Dumps the loaded channels into a specified JSON file.

        Note: if there are no channels loaded, it fetches up to date channels
        from the remote Zato Server.

        :param json_file (str): The JSON file path to dump the channels
        """
        if not len(self.rest_channels):
            self.load_rest_channels()
        with open(json_file, 'w+') as f:
            json.dump(self.rest_channels, f, indent=4, sort_keys=True)

    def channel_to_request_params(self, channel, cluster_id=1):
        """Makes raw channel data compatible for the Zato's
        zato.http-soap.create endpoint.

        :param channel (dict): raw channel data
        :param cluster_id (int): The cluster id to pull/push connections
        :return: (dict)
        """
        request = {
            "cluster_id": cluster_id,
            "is_active": channel.get("is_active"),
            "is_internal": channel.get("is_internal"),
            "name": channel.get("name"),
            "transport": channel.get("transport"),
            "url_path": channel.get("url_path"),
            "cache_expiry": channel.get("cache_expiry"),
            "cache_id": channel.get("cache_id"),
            "content_encoding": channel.get("content_encoding"),
            "content_type": channel.get("content_type"),
            "data_format": channel.get("data_format"),
            "has_rbac": channel.get("has_rbac"),
            "host": channel.get("host"),
            "match_slash": channel.get("match_slash"),
            "merge_url_params_req": channel.get("merge_url_params_req"),
            "method": channel.get("method"),
            "params_pri": channel.get("params_pri"),
            "ping_method": channel.get("ping_method"),
            "pool_size": channel.get("pool_size"),
            "sec_tls_ca_cert_id": channel.get("sec_tls_ca_cert_id"),
            "security_id": channel.get("security_id"),
            "serialization_type": channel.get("serialization_type"),
            "soap_action": channel.get("soap_action"),
            "timeout": channel.get("timeout"),
            "url_params_pri": channel.get("url_params_pri"),
            "service": channel.get("service_name")
        }
        # if that's a incoming service definition
        if channel["connection"] == "channel":
            request.update({
                "connection": "channel",
            })
        else:
            request.update({"connection": "outgoing"})

        return request

    def restore_rest_channels(self, from_file=None,
                              from_list=None, from_registry_instance=None):
        """Restores the saved connection list into the remote Zato server.

        :param from_file (str): A JSON file path includes connections
        :param from_list: (list): A python list of channels
        :param from_registry_instance: (Registry) A registry instance to get
        the old connection definitions.
        """
        channel_list = []
        if from_file:
            with open(from_file, 'r') as f:
                channel_list = json.load(f)
        elif from_list:
            channel_list = from_list
        elif from_registry_instance:
            channel_list = from_registry_instance.rest_channels

        for channel in channel_list:
            self.restore_channel(channel)

    def restore_channel(self, channel):
        """Creates a single channel on the remote Zato server.

        :param channel (dict): Channel data
        """
        response = self.client.invoke(
            "zato.http-soap.create",
            self.channel_to_request_params(channel, self.cluster_id)
        )

        if not response.data:
            details = json.loads(response.details)
            # There must be a better way to do this
            # but it looks like, to understand if a connection already
            # exist in the Zato, you have to parse the stacktrace.
            if 'An object of that name `{}` already exists on this' \
               ' cluster' in details["zato_env"]["details"]:
                logger.info("%s is already defined. ", channel["name"])
        else:
            logger.info("%s added to the connections.", channel["name"])
