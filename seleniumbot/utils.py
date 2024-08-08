import re


class stringutil:
    """
    String class helpers
    """

    @staticmethod
    def decompose_proxy_url(url: str) -> dict:
        """
        Decompose a proxy url

        :param url: proxy url
        :return: proxy info dict {host, port, username, password}
        """
        no_authentication_pattern = r'(?:[https:]+\/\/)?([\w\-\.]+):(\d+)'
        with_authentication_pattern = r'(?:[https:]+\/\/)?(.+):(.+)@([\w\-\.]+):(\d+)'
        proxy = {
            'host': '',
            'port': '',
            'username': '',
            'password': ''
        }

        no_auth_match = re.search(no_authentication_pattern, url)
        with_auth_match = re.search(with_authentication_pattern, url)

        if no_auth_match:
            proxy['host'] = no_auth_match.group(1)
            proxy['port'] = int(no_auth_match.group(2))
        elif with_auth_match:
            proxy['username'] = with_auth_match.group(1)
            proxy['password'] = with_auth_match.group(2)
            proxy['host'] = with_auth_match.group(3)
            proxy['port'] = int(with_auth_match.group(4))

        return proxy
