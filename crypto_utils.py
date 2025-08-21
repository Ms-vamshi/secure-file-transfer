import base64
import os
import tempfile
from typing import Optional, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# Simple container format for encrypted files:
# [ MAGIC(4) | NONCE(12) | CIPHERTEXT(+TAG) ]
MAGIC = b"SFT1"
NONCE_SIZE = 12
KEY_SIZE = 32  # 256-bit AES



def generate_aes256_key() -> bytes:
	"""Generate a random 256-bit AES key.

	Returns:
		bytes: 32-byte random key suitable for AES-256.
	"""
	return os.urandom(KEY_SIZE)


def encode_key_base64(key: bytes) -> str:
	"""Encode a raw key as URL-safe Base64 string without newlines."""
	return base64.urlsafe_b64encode(key).decode("ascii")


def decode_key_base64(key_b64: str) -> bytes:
	"""Decode a URL-safe Base64 key string back to raw bytes."""
	return base64.urlsafe_b64decode(key_b64.encode("ascii"))


def encrypt_file(file_path: str) -> Tuple[str, str]:
	"""Encrypt a file using AES-256-GCM with a randomly generated key.

	The encrypted file is written to a temporary path using a simple
	binary container format: MAGIC + NONCE + CIPHERTEXT(+TAG).

	Args:
		file_path: Path to the plaintext file to encrypt.

	Returns:
		Tuple[str, str]: (encrypted_file_path, key_base64)
	"""
	with open(file_path, "rb") as f:
		plaintext = f.read()

	key = generate_aes256_key()
	nonce = os.urandom(NONCE_SIZE)
	aesgcm = AESGCM(key)
	ciphertext = aesgcm.encrypt(nonce, plaintext, None)

	fd, temp_path = tempfile.mkstemp(suffix=".enc")
	os.close(fd)
	with open(temp_path, "wb") as out:
		out.write(MAGIC)
		out.write(nonce)
		out.write(ciphertext)

	return temp_path, encode_key_base64(key)


def decrypt_file(encrypted_file_path: str, key_base64: str, output_path: Optional[str] = None) -> str:
	"""Decrypt a file produced by encrypt_file using the provided Base64 key.

	Args:
		encrypted_file_path: Path to the encrypted file (MAGIC+NONCE+CIPHERTEXT).
		key_base64: Base64-encoded AES-256 key string.
		output_path: Optional path for the decrypted plaintext.

	Returns:
		str: Path to the decrypted plaintext file.
	"""
	with open(encrypted_file_path, "rb") as f:
		header = f.read(len(MAGIC))
		if header != MAGIC:
			raise ValueError("Invalid encrypted file format: MAGIC mismatch")
		nonce = f.read(NONCE_SIZE)
		ciphertext = f.read()

	key = decode_key_base64(key_base64)
	aesgcm = AESGCM(key)
	plaintext = aesgcm.decrypt(nonce, ciphertext, None)

	if output_path is None:
		if encrypted_file_path.endswith(".enc"):
			output_path = encrypted_file_path[:-4]
		else:
			output_path = encrypted_file_path + ".decrypted"

	with open(output_path, "wb") as out:
		out.write(plaintext)

	return output_path


def encrypt_stream_to_file(file_like, output_path: str) -> Tuple[str, str]:
	"""Encrypt a file-like object using streaming AES-256-GCM and write to output_path.

	Format: [12-byte nonce][ciphertext bytes][16-byte tag]

	Args:
		file_like: A binary file-like object open for reading.
		output_path: Destination path to write the encrypted blob.

	Returns:
		Tuple[str, str]: (output_path, base64_key)
	"""
	key = generate_aes256_key()
	nonce = os.urandom(NONCE_SIZE)
	cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
	encryptor = cipher.encryptor()

	with open(output_path, "wb") as out:
		out.write(nonce)  # no MAGIC for web flow; exact format per spec
		while True:
			chunk = file_like.read(4 * 1024 * 1024)
			if not chunk:
				break
			ct = encryptor.update(chunk)
			if ct:
				out.write(ct)
		encryptor.finalize()
		out.write(encryptor.tag)

	return output_path, encode_key_base64(key)


