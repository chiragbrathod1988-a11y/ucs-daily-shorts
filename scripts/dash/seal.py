"""Encrypt a short secret string (e.g. a signed download URL) so only GitHub Actions (secret UCS_FETCH_KEY) can read it.
X25519 + HKDF-SHA256 + AES-GCM. UCS_FETCH_KEY is a 44-character base64 string; the public half is scripts/dash/fetch_pub.x25519.
Usage: python3 scripts/dash/seal.py "<text>"   -> prints the sealed JSON blob (put it in fetch/*.json as {"sealed": blob, "path": ...})
"""
import sys, os, json, base64, re
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

b64, unb64 = (lambda b: base64.b64encode(b).decode()), base64.b64decode
RAW = serialization.Encoding.Raw, serialization.PublicFormat.Raw

def _kdf(shared):
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"ucs-fetch").derive(shared)

def seal(text):
    pub = X25519PublicKey.from_public_bytes(unb64(open(os.path.join(os.path.dirname(__file__), "fetch_pub.x25519")).read().strip()))
    eph = X25519PrivateKey.generate()
    key, nonce = _kdf(eph.exchange(pub)), os.urandom(12)
    return {"e": b64(eph.public_key().public_bytes(*RAW)), "n": b64(nonce), "c": b64(AESGCM(key).encrypt(nonce, text.encode(), None))}

def unseal(blob):
    txt = re.sub(r"[^A-Za-z0-9+/=]", "", os.environ["UCS_FETCH_KEY"])
    priv = X25519PrivateKey.from_private_bytes(unb64(txt))
    key = _kdf(priv.exchange(X25519PublicKey.from_public_bytes(unb64(blob["e"]))))
    return AESGCM(key).decrypt(unb64(blob["n"]), unb64(blob["c"]), None).decode()

if __name__ == "__main__":
    print(json.dumps(seal(sys.argv[1])))
