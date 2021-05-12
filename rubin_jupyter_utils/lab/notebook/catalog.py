import functools
import requests
import pyvo
import pyvo.auth.authsession
import warnings
from rubin_jupyter_utils.helpers import get_access_token
from rubin_jupyter_utils.config import RubinConfig


def deprecated(new_name=''):
    def deprecated(func):
        """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emitted
        when the function is used."""
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)  # turn off filter
            if new_name:
                warnings.warn(f"Call to deprecated function {func.__name__}.  " +
                              "This function may be removed at any point in the future.  " +
                              f"Please use {new_name} instead.",
                              category=DeprecationWarning,
                              stacklevel=2)
            else:
                warnings.warn(f"Call to deprecated function {func.__name__}.  " +
                              "This function may be removed at any point in the future.",
                              category=DeprecationWarning,
                              stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)  # reset filter
            return func(*args, **kwargs)
        return new_func
    return deprecated


def _get_tap_url():
    rc = RubinConfig()
    tapurl = rc.external_tap_url or (rc.external_instance_url +
                                     rc.tap_route)
    return tapurl


def _get_auth():
    tap_url = _get_tap_url()
    s = requests.Session()
    s.headers["Authorization"] = "Bearer " + get_access_token()
    auth = pyvo.auth.authsession.AuthSession()
    auth.credentials.set("lsst-token", s)
    auth.add_security_method_for_url(tap_url, "lsst-token")
    auth.add_security_method_for_url(tap_url + "/sync", "lsst-token")
    auth.add_security_method_for_url(tap_url + "/async", "lsst-token")
    auth.add_security_method_for_url(tap_url + "/tables", "lsst-token")
    return auth


def get_tap_service():
    return pyvo.dal.TAPService(_get_tap_url(), _get_auth())


@deprecated(new_name="get_tap_service")
def get_catalog():
    return get_tap_service()


def retrieve_query(query_url):
    return pyvo.dal.AsyncTAPJob(query_url, _get_auth())
