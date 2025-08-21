import argparse
import os
import sys

from crypto_utils import encrypt_file
from qr_utils import create_qr_code
from s3_utils import generate_presigned_url, upload_to_s3


def main() -> int:
	parser = argparse.ArgumentParser(description="Secure File Transfer: sender flow")
	parser.add_argument("--file", required=True, help="Path to the local file to encrypt and send")
	parser.add_argument("--bucket", required=True, help="S3 bucket name")
	parser.add_argument("--key-prefix", default="", help="Optional S3 key prefix (e.g., folder path)")
	parser.add_argument("--object-key", default=None, help="Explicit S3 object key (overrides generated key)")
	parser.add_argument("--expires", type=int, default=600, help="Presigned URL expiry in seconds (default: 600)")
	parser.add_argument("--qr-out", default="qr.png", help="Output path for the QR image (default: qr.png)")
	parser.add_argument("--keep-local", action="store_true", help="Keep local encrypted file after upload")
	args = parser.parse_args()

	plaintext_path = args.file
	if not os.path.isfile(plaintext_path):
		print(f"File not found: {plaintext_path}", file=sys.stderr)
		return 1

	print("[1/4] Encrypting...")
	encrypted_path, key_b64 = encrypt_file(plaintext_path)
	print(f"   Encrypted file: {encrypted_path}")
	print("   AES key (base64) – share out-of-band:")
	print(key_b64)

	print("[2/4] Uploading to S3...")
	object_key = upload_to_s3(
		file_path=encrypted_path,
		bucket=args.bucket,
		object_key=args.object_key,
		key_prefix=args.key_prefix,
	)
	print(f"   S3 object key: {object_key}")

	print("[3/4] Generating presigned URL...")
	url = generate_presigned_url(bucket=args.bucket, object_key=object_key, expiry=args.expires)
	print("   Presigned URL (QR will embed this):")
	print(url)

	print("[4/4] Creating QR image...")
	qr_path = create_qr_code(url, output_path=args.qr_out)
	print(f"   QR saved to: {qr_path}")

	if not args.keep_local:
		try:
			os.remove(encrypted_path)
		except OSError:
			pass

	print("Done.")
	return 0


if __name__ == "__main__":
	sys.exit(main())


