"""Encrypt a short secret string (e.g. a signed download URL) so only GitHub Actions (secret UCS_FETCH_KEY) can read it.
Usage: python3 scripts/dash/seal.py "<text>"   -> prints a JSON blob for fetch/*.json  {"sealed": {...}, "path": ...}
       python3 scripts/dash/seal.py --open '<blob json>'  (Actions side; reads UCS_FETCH_KEY env)
"""
import sys, os, json, base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

OAEP = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
b64 = lambda b: base64.b64encode(b).decode()

def seal(text):
    pub = serialization.load_pem_public_key(open(os.path.join(os.path.dirname(__file__), "fetch_pub.pem"), "rb").read())
    key, nonce = AESGCM.generate_key(bit_length=256), os.urandom(12)
    return {"k": b64(pub.encrypt(key, OAEP)), "n": b64(nonce), "c": b64(AESGCM(key).encrypt(nonce, text.encode(), None))}

def _load_key(txt):
    # tolerate pasted keys whose line breaks were lost or changed: rebuild a clean PEM from the base64 body
    import re, textwrap
    body = re.sub(r"-----(BEGIN|END)[A-Z ]*-----", "", txt)
    body = re.sub(r"[^A-Za-z0-9+/=]", "", body)
    pem = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(textwrap.wrap(body, 64)) + "\n-----END PRIVATE KEY-----\n"
    return serialization.load_pem_private_key(pem.encode(), password=None)

def unseal(blob):
    priv = _load_key(os.environ["UCS_FETCH_KEY"])
    key = priv.decrypt(base64.b64decode(blob["k"]), OAEP)
    return AESGCM(key).decrypt(base64.b64decode(blob["n"]), base64.b64decode(blob["c"]), None).decode()

if __name__ == "__main__":
    if sys.argv[1] == "--open":
        print(unseal(json.loads(sys.argv[2])))
    else:
        print(json.dumps(seal(sys.argv[1])))
