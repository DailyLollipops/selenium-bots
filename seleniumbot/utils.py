from urllib.parse import urlparse


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
        proxy = {
            'host': '',
            'port': '',
            'username': '',
            'password': ''
        }

        parsed_url = urlparse(url)

        proxy['host'] = parsed_url.hostname
        proxy['port'] = parsed_url.port

        if parsed_url.username:
            proxy['username'] = parsed_url.username
        if parsed_url.password:
            proxy['password'] = parsed_url.password

        return proxy
