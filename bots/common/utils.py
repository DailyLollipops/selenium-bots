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
