#!/usr/bin/env python

import os
from socket import gethostname

from OpenSSL import crypto
from steamroller import app

cert_path = "data"
if not os.path.exists(cert_path):
    os.makedirs(cert_path)

cert_file_path = os.path.join(cert_path, "cert.pem")
key_file_path = os.path.join(cert_path, "key.pem")

if not os.path.exists(cert_path) or not os.path.exists(key_file_path):

    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().CN = gethostname()
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)

    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha1")

    with open(cert_file_path, "wb") as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_file_path, "wb") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


app.run(
    host="0.0.0.0", threaded=True, ssl_context=(cert_file_path, key_file_path),
)
