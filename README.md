# Secure File Transfer via QR Code

A Flask-based web application that allows users to upload files and generate QR codes for secure file sharing. Files are automatically deleted after 20 minutes using MongoDB GridFS.

## Features

- File upload to MongoDB GridFS
- QR code generation for file download
- Automatic file deletion after 20 minutes
- Modern, responsive UI
- Public file access via QR code

## Prerequisites

- Python 3.7+
- MongoDB Atlas account (free tier available)
- MongoDB connection string

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd secure-file-transfer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MongoDB Atlas:
   - Create a free account at https://www.mongodb.com/cloud/atlas
   - Create a new cluster (free tier is sufficient)
   - Click "Connect" and choose "Connect your application"
   - Copy the connection string

4. Create a `.env` file in the project root with your MongoDB connection string:
```
MONGODB_URI=your_mongodb_connection_string
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Open the web application in your browser
2. Click "Select File" or drag and drop a file to upload
3. Click "Upload File"
4. A QR code will be generated for the file
5. Share the QR code with others to allow them to download the file
6. The file will be automatically deleted after 20 minutes

## Security Considerations

- Files are stored in MongoDB GridFS
- Files are automatically deleted after 20 minutes using TTL index
- Each file gets a unique identifier
- File metadata is stored in MongoDB

## Deployment

1. Deploy to Render/Vercel:
   - Create a new web service
   - Connect your GitHub repository
   - Set environment variables
   - Deploy

2. MongoDB Atlas:
   - Use the free tier cluster
   - Set up network access to allow connections from your deployment
   - Monitor usage to stay within free tier limits

## License

MIT License #   s e c u r e - f i l e - t r a n s f e r  
 