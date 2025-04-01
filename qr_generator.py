import pyqrcode
import base64
from io import BytesIO
from PIL import Image

class QRGenerator:
    @staticmethod
    def generate_qr(url):
        """Generate QR code for the given URL and return it as base64 string."""
        try:
            # Create QR code instance
            qr = pyqrcode.create(url)
            
            # Create an image from the QR Code
            qr_image = qr.png_as_base64_str(scale=8)
            
            return qr_image
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            raise 