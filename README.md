# 🔒 Secure File Transfer with Mobile QR Code Download

The Secure File Transfer App is a production-ready platform that enables users to upload and share files safely using QR codes, presigned URLs, and auto-expiring links.

This project solves the common problem of transferring files quickly without exposing them to long-term storage risks.
It is minimal, secure, scalable, and cloud-native — making it ideal for both academic evaluation and real-world use.
## ✨ Features

- **📁 File Upload**: Drag & drop interface for easy file uploads
- 🔐 AWS S3 Secure Storage using presigned URLs
- **☁️ S3 Integration**: Secure cloud storage with pre-signed URLs
- **📱 QR Code Generation**: Automatic QR code creation for each file
- **📲 Mobile Download**: Scan QR codes to download files directly to mobile devices
- **⏰ Time-Limited Access**: Configurable expiration times for download links
- **🛡️ Rate Limiting**: Protection against abuse
- **🎨 Modern UI**: Clean, responsive design

## 🚀 Live Demo

## Secure File Transfer App is now live!
🔗 Live URL: https://secure-file-transfer.up.railway.app/

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- AWS S3 bucket
- AWS credentials configured

### Installation

1. **Clone and setup:**
```bash
git clone <your-repo>
cd securefiletransfer
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables:**
Create a `.env` file:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
AWS_BUCKET=your-s3-bucket-name
FLASK_SECRET_KEY=your-secret-key
DELETE_TOKEN=your-delete-token
PRESIGN_EXPIRY_SECONDS=600
PUBLIC_URL=http://localhost:5000
```

3. **Set up public access (for mobile QR codes):**
```bash

python app.py

```

4. **Run the server:**
```bash
python start_server.py
```

5. **Access the application:**
Open your browser to `http://localhost:5000`

## 📱 How It Works

### Upload Process
1. **Upload File**: Use the web interface to upload any file (up to 2GB)
2. **Encryption**: File is encrypted using AES-GCM encryption
3. **S3 Upload**: Encrypted file is stored in your S3 bucket
4. **Pre-signed URL**: A time-limited download URL is generated
5. **QR Code**: A QR code is created containing the download link
6. **Display**: QR code is shown on the web page

### Download Process (Mobile)
1. **Scan QR Code**: Use any QR code scanner app on your mobile device
2. **Automatic Download**: The file automatically downloads to your device
3. **Decryption**: File is decrypted on-the-fly during download
4. **Security**: Link expires based on your settings

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes | - |
| `AWS_REGION` | AWS region | Yes | - |
| `AWS_BUCKET` | S3 bucket name | Yes | - |
| `FLASK_SECRET_KEY` | Flask secret key | Yes | - |
| `DELETE_TOKEN` | Token for file deletion | No | - |
| `PRESIGN_EXPIRY_SECONDS` | Link expiration time | No | 600 (10 min) |
| `PUBLIC_URL` | Public URL for mobile access | No | http://localhost:5000 |

### File Limits
- **Maximum file size**: 2GB
- **Supported formats**: All file types
- **Expiry options**: 1 minute to 7 days

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Web UI    │───▶│  Flask App  │───▶│   S3 Bucket │
│             │    │             │    │             │
│ Drag & Drop │    │ Encryption  │    │ Encrypted   │
│ QR Display  │    │ QR Gen      │    │ Files       │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Mobile    │    │   QR Code   │    │  Download   │
│   Device    │◀───│   Scanner   │◀───│   Link      │
│             │    │             │    │             │
│ Auto Download│   │ Scan QR     │    │ Decryption  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📁 Project Structure

```
securefiletransfer/
├── app.py              # Main Flask application
├── crypto_utils.py     # AES-GCM encryption/decryption
├── qr_utils.py         # QR code generation
├── s3_utils.py         # S3 upload/download utilities
├── start_server.py     # Local server runner
├── templates/          # HTML templates
│   ├── index.html      # Upload page
│   └── result.html     # QR code display page
├── static/             # Static files
│   ├── style.css       # Modern CSS styling
│   └── qr/             # Generated QR codes
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🔒 Security Features

- **AES-GCM Encryption**: Military-grade encryption for all files
- **Pre-signed URLs**: Time-limited access to S3 objects
- **Rate Limiting**: Protection against abuse (30 requests per minute)
- **Secure Headers**: Proper content disposition and caching headers
- **Input Validation**: Comprehensive validation of all inputs
- **No Plaintext Storage**: Only encrypted files are stored in S3

## 📱 Mobile Usage Guide

### For Users
1. **Upload a file** using the web interface at `http://localhost:5000`
2. **Scan the QR code** with any QR scanner app (Google Lens, Camera app, etc.)
3. **File automatically downloads** to your mobile device
4. **No additional apps required** - works with any QR scanner

### For Developers
- The QR code contains a URL like: `http://localhost:5000/decrypt?url=...&key=...&fname=...`
- Mobile devices access this URL to download and decrypt files
- The `/decrypt` endpoint handles the entire download and decryption process

## 🚀 Deployment Options

### Local Development
```bash
python start_server.py
```

### Production
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
```

## 🛠️ Development

### Running Tests
```bash
# Test S3 connectivity
python test_s3.py

# Test encryption
python -c "from crypto_utils import *; print('Encryption working')"
```

### Adding Features
- **New file types**: Modify `mimetypes` handling in `app.py`
- **Custom expiry**: Update the expiry options in `templates/index.html`
- **UI changes**: Modify `static/style.css` and templates

## 🔧 AWS Setup

### S3 Bucket Configuration
1. Create an S3 bucket
2. Configure CORS if needed
3. Set up lifecycle rules for automatic cleanup

### IAM Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket/uploads/*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::your-bucket",
      "Condition": {"StringLike": {"s3:prefix": ["uploads/*"]}}
    }
  ]
}
```

## 🆘 Troubleshooting

### Common Issues
1. **AWS credentials not found**: Check your `.env` file
2. **S3 upload fails**: Verify bucket permissions and region
3. **QR code not working**: Ensure mobile device can access `localhost:5000`
4. **File too large**: Check the 2GB limit

### Debug Mode
The app runs in debug mode by default. Check the console for detailed error messages.

## 📄 License

This project is licensed under the MIT License.

---

**🔒 Secure File Transfer** - Making file sharing simple and secure! 📱

**Key Benefits:**
- ✅ No mobile app required
- ✅ Works on any mobile device
- ✅ Secure encryption
- ✅ Time-limited access
- ✅ Easy to use web interface


## 📬 Contact

If you want to improve or collaborate, feel free to connect!

## Maila Sai Vamshi

📧 mailasaivamshi02@gmail.com

🔗 GitHub: https://github.com/Ms-vamshi

🔗 LinkedIn: https://www.linkedin.com/in/sai-vamshi23/
