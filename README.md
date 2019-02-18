# py-consent-sign
### Functional examples of Signicat Consent Signature

---

These are **functional examples** of Consent Signature. It does not illustrate how to implement the solution in a production environment, it merely illustrates the API calls required to make the flow work as expected. It can be viewed as a jumping-off point for your app implementation.

This example follows the documentation at (TODO).

PS: Documentation will be made available as soon as it's ready.

**Dependencies**:

* Python 3
* Built in: sys, random, time, urllib.parse
* [Requests](http://docs.python-requests.org/en/master/): HTTP for Humans.

### Supported eIDs.

* [nbid-consent-sign.py](./nbid-consent-sign.py): Norwegian BankID on mobile (BankID på Mobil)
* [sbid-consent-sign.py](./sbid-consent-sign.py): Swedish BankID on mobile (BankID på Mobil)

To be able to use our Consent Signature solution, the eID must fullfil several technical requirements related to mobile integration. So far Signicat has created inapp methods for only Norwegian and Swedish BankID.

### Flow

Preparations:
* Fetch JWKs - prepare the public key.
* Prepare the encrypted payload.
* Prepare PKCE (optional)

Steps:
1. Call /authorize 
2. Poll statusUri until status=finished (sbid: collectUrl until progressStatus=COMPLETE)
3. Call completeUri (sbid: completeUrl) - the last redirect will contain CODE and STATE.
4. Call /token end-point as normal (using CODE we got in STEP 3)
5. Call /userinfo with access token. (optional)
6. Call /signature with access token, to get the ltv-sdo document.


Note: All steps should be performed in backend. Alternatively Step 1-3 can be performed in a mobile app. Step 4 & 5 must always be performed at a backend (the web service hosted at your redirect URI). 

### Application Usage

**Norwegian BankID** ([nbid-consent-sign.py](./nbid-consent-sign.py))

The variable ```payload['login_hint']``` needs to be changed to a valid Norwegian BankID test-user. This test-user has to be enabled for BankID on a mobile device!
Format: ```["birthdate-ddmmyy", "phone-nnnnnnnn"]```

Once you have changed these variable, you can run it with ```python3 nbid-consent-sign.py```.

**Swedish BankID** ([sbid-consent-sign.py](./sbid-consent-sign.py))

The variable ```payload['login_hint']``` needs to be changed to a valid Norwegian BankID test-user. This test-user has to be enabled for BankID on a mobile device!
Format: subject-yyyymmddnnnn

Once you have changed this variable, you can run it with ```python3 sbid-consent-sign.py```.

**Security Concerns**

There are certain key concepts to keep in mind to be able to achive a good level of security when implementing consent signing.
* [Proof Key for Code Exchange](https://tools.ietf.org/html/rfc7636): Signicat feels that a code interception attack is likely if the flow is ran in a mobile device. As such it is **strongly recommended** that you implement this extension for OAuth/OIDC (supported by default on Signicat's OIDC clients). *The code examples in this repo already has PKCE implemented!*
* Unless you have specifically hardened security of your mobile application, you have to consider it somewhat unsafe. *OIDC tokens and client secrets provided by Signicat should not be stored in your app.*
* As mentioned earlier step 4 & 5 **should not** be performed in-app. 
* General hardening of mobile applications should also be considered. See for instance AppSamurai blog post: [12 Various Ways To Ensure Mobile Application Security](https://appsamurai.com/12-various-ways-to-ensure-mobile-application-security/)

### References

[Norwegian BankID: Test Information](https://developer.signicat.com/id-methods/norwegian-bankid-on-mobile/#test-information).

[Swedish BankID: Test Information](https://developer.signicat.com/id-methods/swedish-bankid/#test-information).

For general information about the Authentication service, please refer to [Get Started With Authentication](https://developer.signicat.com/documentation/authentication/get-started-with-authentication/).

### Specifications
* [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
* [JSON Web Encryption (JWE)](https://tools.ietf.org/html/rfc7516)
* [JSON Web Key (JWK)](https://tools.ietf.org/html/rfc7517)
* [Proof Key for Code Exchange](https://tools.ietf.org/html/rfc7636)