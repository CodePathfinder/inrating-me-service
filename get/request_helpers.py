from .models import Users
from . import const
import time


def timestamp_token_verification(data):
    # check if authorization token is not expired

    try:
        iat = data.get('iat')
        exp = data.get('exp')
    except Exception:
        return False
    else:
        now = int(time.time())
        if iat >= now or exp <= now:
            return False
        else:
            return True


def verify_user_status(id, cuid):
    unavailable_reasons = [item[0]
                           for item in const.unavailable_user_status_codes.items()]
    unaval_reason = ''
    user = Users.objects.filter(id=id).first()
    if not user:
        unaval_reason = 'not_found'
        return ((None, unaval_reason))
    elif id == cuid:
        return ((cuid, unaval_reason))
    elif user.status.replace(' ', '_') in unavailable_reasons:
        unaval_reason = user.status.replace(' ', '_')
        return ((id, unaval_reason))
    elif user.userblacklist_set.filter(blocked_user_id=cuid).exists():
        unaval_reason = 'blacklist'
        return ((id, unaval_reason))
    else:
        return ((id, unaval_reason))
