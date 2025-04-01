from flask import Flask, request, jsonify, send_file, render_template
from db_config import fs
from qr_generator import QRGenerator
import os
from datetime import datetime
import io

app = Flask(__name__)
qr_generator = QRGenerator()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and generate QR code."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Store file in GridFS
        file_id = fs.put(
            file,
            filename=file.filename,
            content_type=file.content_type,
            uploadDate=datetime.utcnow()
        )
        
        # Generate download URL
        download_url = f"{request.host_url}download/{str(file_id)}"
        
        # Generate QR code
        qr_code = qr_generator.generate_qr(download_url)
        
        return jsonify({
            'file_id': str(file_id),
            'filename': file.filename,
            'download_url': download_url,
            'qr_code': qr_code
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Handle file download."""
    try:
        # Get file from GridFS
        file_data = fs.get(file_id)
        
        # Create response
        return send_file(
            io.BytesIO(file_data.read()),
            mimetype=file_data.content_type,
            as_attachment=True,
            download_name=file_data.filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Handle manual file deletion."""
    try:
        # Delete file from GridFS
        fs.delete(file_id)
        return jsonify({'message': 'File deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 