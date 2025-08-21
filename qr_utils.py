from typing import Optional

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def create_qr_code(url: str, output_path: str = "qr.png", box_size: int = 10, border: int = 4) -> str:
	"""Generate and save a QR code image containing the provided URL.

	Args:
		url: The URL to encode in the QR.
		output_path: Where to save the generated QR image.
		box_size: Pixel size of each QR module.
		border: Border width (modules).

	Returns:
		str: The path to the generated QR image.
	"""
	qr = qrcode.QRCode(
		version=None,
		error_correction=ERROR_CORRECT_M,
		box_size=box_size,
		border=border,
	)
	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image(fill_color="black", back_color="white")
	img.save(output_path)
	return output_path



