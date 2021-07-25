from time import time


def timestamp_token_verification(data):
    """ Token verification: is expired ? """

    try:
        iat = data.get('iat')
        exp = data.get('exp')
    except Exception:
        return False
    else:
        now = int(time())
        if iat >= now or exp <= now:
            return False
        else:
            return True
