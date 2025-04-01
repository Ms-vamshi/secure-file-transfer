from pymongo import MongoClient
from gridfs import GridFS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db():
    """Initialize MongoDB connection and GridFS."""
    try:
        # Connect to MongoDB Atlas
        client = MongoClient('mongodb+srv://Ms-vamshi:f4cd7ej7nAdCcJec@cluster0.wqnf7ru.mongodb.net/')
        
        # Create/get the file_transfer database
        db = client.file_transfer
        
        # Initialize GridFS
        fs = GridFS(db)
        
        # Create TTL index
        db.fs.files.create_index(
            "uploadDate",
            expireAfterSeconds=1200  # 20 minutes
        )
        
        return db, fs
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

# Initialize database connection
db, fs = get_db() 