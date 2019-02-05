import sys
import requests
import random
import urllib.parse as urlparse
from time import sleep
from inapp_funcs import encryptRequest, findJWK
from pkce import code_verifier, code_challenge


# Prepare PKCE (https://tools.ietf.org/html/rfc7636)
verifier = code_verifier(40)
challenge = code_challenge(verifier)
print("PKCE: verifier='{}', challenge='{}'".format(verifier, challenge))

# Fetch jwks.json, prepare the public key.
url = "https://preprod.signicat.com/oidc/jwks.json"
r = requests.get(url)
res = r.json()["keys"]
jwk_pub = findJWK(res)

""" 'login_hint' needs to be the details of a Norwegian BankID test-user setup with "BankID på Mobil"!
    See https://developer.signicat.com/id-methods/norwegian-bankid-on-mobile/#test-information
    Format: ["birthdate-ddmmyy", "phone-nnnnnnnn"]
"""
# Prepare and encrypt the payload.
payload = {
    "login_hint": ["birthdate-ddmmyy", "phone-nnnnnnnn"],
    "ui_locales": "nb",
    "scope": "openid profile signicat.sign",
    "signicat_signtext": "I confirm my purchase of broadband subscription Medium500.",
    "acr_values": "urn:signicat:oidc:method:nbid-inapp-sign",
    "response_type":"code",
    "redirect_uri": "https://labs.signicat.com/redirect",
    "state": ''.join(random.choice('ABCDEF0123456789') for _ in range(8)),
    "client_id": "demo-inapp-sign",
    "code_challenge_method": "S256",
    "code_challenge": challenge.decode()
}
print("\nPayload: {}".format(payload))
enc = encryptRequest(jwk_pub, payload)
print("\nEncrypted payload: {}".format(enc))

# STEP 1: Call authorize using method "nbid-inapp-sign"
headers1 = {'Accept': 'application/json'}
url1 = ('https://preprod.signicat.com/oidc/authorize?request={}'.format(enc))
r1 = requests.get(url1, headers=headers1)
jar = r1.cookies # !IMPORTANT! Saves all cookies - to be used in future requests.
res1 = r1.json()
print("Authorize Response: {}".format(res1))

# STEP 2: Poll collectUrl until status=finished
url2 = res1['statusUri']
PS = {'status': None}
print("\nPolling...")
while 'finished' not in PS: # Check if finished, if not sleep 5s and check again.
    sleep(5)
    res2 = requests.get(url2, headers=headers1, cookies=jar).json()
    PS = res2['status']
    print("  -- Status: {}".format(PS))
print("collectUrl Response: {}".format(res2))

# STEP 3: Call completeUrl - the last redirect will contain CODE and STATE.
url3 = res2['completeUri']
r3 = requests.get(url3, cookies=jar) # requests.get() method automatically follows redirects.
res3 = r3.history[-1].headers['Location'] # Get the LAST of the redirects. This contains code and state.
res3_params = urlparse.parse_qs(urlparse.urlparse(res3).query)
print("\nFinal redirect from completeURL: {}".format(res3))
print("  -- CODE: '{}'".format(res3_params['code'][0]))
print("  -- STATE: '{}'".format(res3_params['state'][0]))

# STEP 4: Call /token end-point as normal (using CODE we got in STEP 3)
headers2 = {'Authorization': 'Basic ZGVtby1pbmFwcC1zaWduOm1xWi1fNzUtZjJ3TnNpUVRPTmI3T240YUFaN3pjMjE4bXJSVmsxb3VmYTg='}
payload = {
    'client_id': 'demo-inapp-sign',
    'redirect_uri': 'https://labs.signicat.com/redirect',
    'grant_type': 'authorization_code',
    'code_verifier': verifier.decode(),
    'code': res3_params['code'][0]
}
res4 = requests.post('https://preprod.signicat.com/oidc/token', data=payload, headers=headers2).json()
token = res4['access_token'] # Access token!
print("\nAccess Token: {} ... (Truncated {} Bytes)".format(token[:33], len(token)-33))

# STEP 5 (optional): Call /userinfo with access token.
headers3 = {'Authorization': 'Bearer ' + token}
res5 = requests.get('https://preprod.signicat.com/oidc/userinfo', headers=headers3).json()
print("UserInfo Response: {}".format(res5))

# STEP 6: Call /signature with access token, to get the ltv-sdo document.
headers3 = {'Authorization': 'Bearer ' + token}
res5 = requests.get('https://preprod.signicat.com/oidc/signature', headers=headers3).text
print("\nLTV-SDO: {}... (Truncated {} Bytes)".format(res5[:100], len(res5)-100))

# Saving XML to file.
try:
    with open("ltv-sdo.xml","w") as fp:
        fp.write(res5)
    print("\nWrote file : {} to current directory".format("ltv-sdo.xml"))
except:
    print("Couldn't write file, something went wrong...")
