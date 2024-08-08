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
    

class dictutils:
    """
    Dictionary utility helper
    """

    @staticmethod
    def get(dictionary: dict, *keys: str, default=None,):
        """
        Traverse a dictionary in a tree-like structure

        :param *keys: Keys to search
        :param default: Value to return if key not found else raise KeyError
        :return: Value
        """
        current_value = dictionary
        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                if default:
                    return default
                raise KeyError(f'Key not found: {key}')
        return current_value
    
    @staticmethod
    def map_key_value(keys: list, values: list) -> dict:
        """
        Map a values to keys.

        :param keys: List of keys
        :param values: List of values
        :return: Mapped dictionary
        """
        result_dict = dict(zip(keys, values))
        return result_dict

    @staticmethod
    def does_keys_exists(dictionary: dict, keys: list[str], strict: bool = True) -> bool:
        """
        Check if all keys exists in the input dictionary

        :param dictionary: Dictionary to check
        :param keys: List of keys to validate
        :param strict: Should all keys exist in the dictionary
        """

        if strict:
            for key in keys:
                if not key in dictionary.keys():
                    return False
            return True
        
        else:
            for key in keys:
                if key in dictionary.keys():
                    return True
            return False
