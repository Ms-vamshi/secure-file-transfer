import os
import tempfile
import time
from uuid import uuid4

from flask import Flask, render_template, request, abort, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from qr_utils import create_qr_code
from s3_utils import generate_presigned_url, upload_to_s3, delete_from_s3


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(16))
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB

AWS_REGION = os.getenv('AWS_REGION')
AWS_BUCKET = os.getenv('AWS_BUCKET')
DEFAULT_EXPIRY = int(os.getenv('PRESIGN_EXPIRY_SECONDS', '600'))
DELETE_TOKEN = os.getenv('DELETE_TOKEN', '')

# For mobile QR code access - you can set this to your public URL
# Options:
# 1. Use ngrok: https://your-ngrok-url.ngrok.io
# 2. Use your public domain: https://your-domain.com
# 3. Use localhost (only works if mobile is on same network)
PUBLIC_URL = os.getenv('PUBLIC_URL', 'http://localhost:5000')

os.makedirs('static/qr', exist_ok=True)
os.makedirs('tmp', exist_ok=True)
os.makedirs('uploads', exist_ok=True)


# Simple in-memory rate limit for /decrypt
REQUEST_WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 30
_request_log = {}


def _rate_limited(ip: str) -> bool:
    now = time.time()
    window_start = now - REQUEST_WINDOW_SECONDS
    reqs = _request_log.get(ip, [])
    reqs = [t for t in reqs if t >= window_start]
    if len(reqs) >= MAX_REQUESTS_PER_WINDOW:
        _request_log[ip] = reqs
        return True
    reqs.append(now)
    _request_log[ip] = reqs
    return False


@app.get("/health")
def health():
    return "OK", 200


@app.get("/")
def index():
    return render_template("index.html", default_expiry=DEFAULT_EXPIRY)


@app.post("/upload")
def upload():
    """
    Handle file upload, S3 storage, and QR code generation.
    This creates a complete secure file transfer workflow.
    """
    file = request.files.get('file')
    expiry = request.form.get('expiry', type=int) or DEFAULT_EXPIRY
    expiry = max(60, min(604800, expiry))  # 1 minute to 7 days
    
    if not file or file.filename == '':
        abort(400, description="Missing file")
    if not AWS_BUCKET:
        abort(500, description="Server not configured (AWS_BUCKET)")

    original_filename = secure_filename(file.filename)
    if not original_filename:
        abort(400, description="Invalid filename")

    # Step 1: Save plaintext to a temporary file (no real encryption)
    suffix = os.path.splitext(original_filename)[1] or ''
    plaintext_tmp_fd, plaintext_tmp_path = tempfile.mkstemp(dir='tmp', suffix=suffix)
    os.close(plaintext_tmp_fd)

    try:
        # Copy upload stream to temp file without persisting in memory
        with file.stream as in_stream, open(plaintext_tmp_path, 'wb') as out:
            while True:
                chunk = in_stream.read(4 * 1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)

        # Step 2: Upload to S3 with unique identifier
        uuid_part = uuid4().hex
        object_key = f"uploads/{uuid_part}/{original_filename}"
        
        upload_to_s3(
            file_path=plaintext_tmp_path,
            bucket=AWS_BUCKET,
            object_key=object_key,
            key_prefix="",
            extra_args={
                "ServerSideEncryption": "AES256",
            },
        )

        # Step 3: Generate pre-signed URL for direct S3 download
        disposition = f"attachment; filename=\"{original_filename}\""
        presigned_url = generate_presigned_url(
            bucket=AWS_BUCKET,
            object_key=object_key,
            expiry=expiry,
            response_headers={
                "ResponseContentDisposition": disposition,
                "ResponseContentType": "application/octet-stream",
            },
        )

        # Step 4: QR should contain the S3 presigned URL directly (works over public internet)
        download_link = presigned_url

        # Step 5: Generate QR code image
        qr_filename = f"{uuid_part}.png"
        qr_path = os.path.join('static', 'qr', qr_filename)
        create_qr_code(download_link, output_path=qr_path)

        # Step 6: Return the result page with QR code
        return render_template(
            "result.html",
            qr_image_url=url_for('static', filename=f"qr/{qr_filename}"),
            expiry_seconds=expiry,
            decrypt_link=download_link,
            bucket=AWS_BUCKET,
            object_key=object_key,
            filename=original_filename,
        )
        
    finally:
        # Clean up temporary file
        try:
            os.remove(plaintext_tmp_path)
        except OSError:
            pass


@app.get("/fake-decrypt")
def fake_decrypt():
    """Show a fake decryption screen then redirect to S3 presigned URL."""
    redirect_url = request.args.get('url')
    filename = request.args.get('fname', '')
    if not redirect_url:
        abort(400, description="Missing url")
    return render_template("decrypt.html", redirect_url=redirect_url, filename=filename)


@app.post("/delete")
def delete():
    """Delete a file from S3 (optional cleanup)"""
    token = request.form.get('token') or request.headers.get('X-Delete-Token')
    bucket = request.form.get('bucket') or request.json.get('bucket') if request.is_json else request.form.get('bucket')
    object_key = request.form.get('key') or request.json.get('key') if request.is_json else request.form.get('key')
    
    if not token or token != DELETE_TOKEN:
        abort(401, description="Unauthorized")
    if not bucket or not object_key:
        abort(400, description="Missing bucket or key")
    
    try:
        delete_from_s3(bucket, object_key)
        return {"status": "deleted"}
    except Exception as e:
        abort(400, description=str(e))


if __name__ == '__main__':
    # Set debug mode for local development
    app.debug = True
    print("🔒 Starting Secure File Transfer Server...")
    print("📱 QR Code functionality is ready!")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📋 Make sure your .env file has the required AWS credentials")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
