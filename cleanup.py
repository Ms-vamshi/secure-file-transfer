import argparse
import sys

from s3_utils import delete_from_s3


def main() -> int:
	parser = argparse.ArgumentParser(description="Delete an S3 object used in secure transfer")
	parser.add_argument("--bucket", required=True, help="S3 bucket name")
	parser.add_argument("--key", required=True, help="S3 object key to delete")
	args = parser.parse_args()

	delete_from_s3(args.bucket, args.key)
	print("Deleted.")
	return 0


if __name__ == "__main__":
	sys.exit(main())



