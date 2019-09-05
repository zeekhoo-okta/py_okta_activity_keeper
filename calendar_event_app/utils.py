from builtins import str
import six


def dict_to_query_params(d):
    if d is None or len(d) == 0:
        return ''

    param_list = [param + '=' + (str(value).lower() if type(value) == bool else str(value))
                  for param, value in six.iteritems(d) if value is not None]
    return '?' + "&".join(param_list)