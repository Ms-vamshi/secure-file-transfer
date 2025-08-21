import argparse
import os
import sys
import tempfile

import requests

from crypto_utils import decrypt_file


def download_to_temp(url: str) -> str:
	"""Download a URL to a temporary file and return its path."""
	resp = requests.get(url, stream=True, timeout=60)
	resp.raise_for_status()
	fd, temp_path = tempfile.mkstemp(suffix=".enc")
	os.close(fd)
	with open(temp_path, "wb") as f:
		for chunk in resp.iter_content(chunk_size=1024 * 1024):
			if chunk:
				f.write(chunk)
	return temp_path


def main() -> int:
	parser = argparse.ArgumentParser(description="Secure File Transfer: receiver flow")
	parser.add_argument("--url", required=True, help="Presigned URL to the encrypted object")
	parser.add_argument("--key-base64", required=True, help="AES key in base64 (provided out-of-band)")
	parser.add_argument("--output", required=False, help="Output path for decrypted file")
	args = parser.parse_args()

	print("[1/3] Downloading encrypted file...")
	encrypted_path = download_to_temp(args.url)
	print(f"   Downloaded to: {encrypted_path}")

	print("[2/3] Decrypting...")
	out_path = decrypt_file(encrypted_path, args.key_base64, args.output)
	print(f"   Decrypted to: {out_path}")

	print("[3/3] Cleaning up temp...")
	try:
		os.remove(encrypted_path)
	except OSError:
		pass

	print("Done.")
	return 0


if __name__ == "__main__":
	sys.exit(main())



