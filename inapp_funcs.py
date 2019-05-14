import json
from jwcrypto import jwk, jwe

def findJWK(keys):
    for k in keys:
        if 'RSA' in k["kty"] and 'enc' in k["use"]:
            return k
    
""" See documentation:
    https://jwcrypto.readthedocs.io/en/latest/jwe.html#examples
    https://jwcrypto.readthedocs.io/en/latest/jwk.html#examples """
def encryptRequest(jwk_pub, payload):
    public_key = jwk.JWK()
    public_key.import_key(**jwk_pub)
    payload_bytes = json.dumps(payload).encode('utf-8')
    protected_header = {
        "alg": jwk_pub["alg"],
        "enc": "A256CBC-HS512",
        "typ": "JWT",
        "kid": jwk_pub["kid"],
    }
    jwetoken = jwe.JWE(payload_bytes, recipient=public_key, protected=protected_header)
    enc = jwetoken.serialize(compact=True)
    return enc