from hashlib import sha1
import base64
import hmac


def compute_signature(token, uri, data):
        """Compute the signature for a given request

        :param uri: full URI for request on API
        :param params: post vars sent with the request
        :returns: The computed signature
        """
        s = uri.split('://')[1]
        if data:
            if type(data) is dict:
                d = sorted(data, key=data.get)
                for k in d:
                    s += k + d[k]
            if type(data) is str:
                s += data
        # compute signature and compare signatures
        mac = hmac.new(token, s.encode("utf-8"), sha1)
        computed = base64.b64encode(mac.digest())
        return computed.strip()


# Definie a exception class to report errors (handy for debugging)
class InvalidMessageException(Exception):
    """Raised when pdu2json cannot properly format the PDU submitted
    :param pdu_exception: the original exception raised by pdu2json
    """
    status_code = 400

    def __init__(self, error, status_code=None, payload=None):
        Exception.__init__(self)
        self.error = error
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.error
        return rv
