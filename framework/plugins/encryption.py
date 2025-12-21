import base64
import hashlib
import hmac
from typing import Any, Dict

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .base import BasePlugin


class RSAEncryptPlugin(BasePlugin):

    def __init__(self):
        super().__init__("rsa_encrypt")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        public_key_pem = config.get("public_key") or context.get("rsa_public_key")

        if not public_key_pem:
            return base64.b64encode(str(input_data).encode()).decode()

        try:
            rsa_key = RSA.import_key(public_key_pem)
            cipher = PKCS1_v1_5.new(rsa_key)
            data_bytes = str(input_data).encode("utf-8")

            max_length = rsa_key.size_in_bytes() - 11
            if len(data_bytes) > max_length:
                raise ValueError(
                    f"Data too long for RSA encryption: {len(data_bytes)} > {max_length}"
                )

            encrypted_data = cipher.encrypt(data_bytes)
            return base64.b64encode(encrypted_data).decode()

        except Exception as e:
            import logging

            logging.error(f"RSA encryption failed: {e}")
            return base64.b64encode(str(input_data).encode()).decode()


class HMACPlugin(BasePlugin):

    def __init__(self):
        super().__init__("hmac")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        key = config.get("key", "default_key").encode()
        algorithm = config.get("algorithm", "sha256")

        if algorithm == "sha256":
            hash_func = hashlib.sha256
        elif algorithm == "sha1":
            hash_func = hashlib.sha1
        elif algorithm == "md5":
            hash_func = hashlib.md5
        else:
            hash_func = hashlib.sha256

        return hmac.new(key, str(input_data).encode(), hash_func).hexdigest()


class SHA256Plugin(BasePlugin):

    def __init__(self):
        super().__init__("sha256")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        return hashlib.sha256(str(input_data).encode()).hexdigest()


class Base64EncodePlugin(BasePlugin):

    def __init__(self):
        super().__init__("base64_encode")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        return base64.b64encode(str(input_data).encode()).decode()


class Base64DecodePlugin(BasePlugin):

    def __init__(self):
        super().__init__("base64_decode")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        return base64.b64decode(str(input_data)).decode()
