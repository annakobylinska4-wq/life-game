"""
S3 Storage module for game data persistence
Provides seamless fallback to local storage for development
"""
import json
import os
import boto3
from botocore.exceptions import ClientError


class S3Storage:
    """Handles reading/writing game data to S3 with local fallback"""

    def __init__(self, bucket_name=None, region_name=None):
        """
        Initialize S3 storage

        Args:
            bucket_name: S3 bucket name (if None, uses local storage)
            region_name: AWS region
        """
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME')
        self.region_name = region_name or os.environ.get('AWS_REGION', 'eu-north-1')
        self.client = None
        self._use_s3 = bool(self.bucket_name)

        if self._use_s3:
            print(f"S3 Storage initialized: bucket={self.bucket_name}, region={self.region_name}")
        else:
            print("S3 Storage: No bucket configured, using local storage")

    def _get_client(self):
        """Lazy initialization of boto3 S3 client"""
        if self.client is None and self._use_s3:
            self.client = boto3.client('s3', region_name=self.region_name)
        return self.client

    def _s3_key(self, filename):
        """Convert filename to S3 key"""
        return f"data/{filename}"

    def read_json(self, filename, local_path=None):
        """
        Read JSON data from S3 or local file

        Args:
            filename: Name of the file (e.g., 'game_states.json')
            local_path: Local file path for fallback

        Returns:
            dict: Parsed JSON data, or empty dict if not found
        """
        if self._use_s3:
            try:
                client = self._get_client()
                response = client.get_object(
                    Bucket=self.bucket_name,
                    Key=self._s3_key(filename)
                )
                content = response['Body'].read().decode('utf-8')
                return json.loads(content)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    # File doesn't exist yet, return empty dict
                    return {}
                else:
                    print(f"S3 read error for {filename}: {e}")
                    # Fall back to local if S3 fails
                    if local_path and os.path.exists(local_path):
                        with open(local_path, 'r') as f:
                            return json.load(f)
                    return {}
            except Exception as e:
                print(f"Unexpected S3 read error for {filename}: {e}")
                if local_path and os.path.exists(local_path):
                    with open(local_path, 'r') as f:
                        return json.load(f)
                return {}
        else:
            # Local storage
            if local_path and os.path.exists(local_path):
                with open(local_path, 'r') as f:
                    return json.load(f)
            return {}

    def write_json(self, filename, data, local_path=None):
        """
        Write JSON data to S3 or local file

        Args:
            filename: Name of the file (e.g., 'game_states.json')
            data: Dictionary to write
            local_path: Local file path for fallback

        Returns:
            bool: True if successful
        """
        json_content = json.dumps(data, indent=2)

        if self._use_s3:
            try:
                client = self._get_client()
                client.put_object(
                    Bucket=self.bucket_name,
                    Key=self._s3_key(filename),
                    Body=json_content.encode('utf-8'),
                    ContentType='application/json'
                )
                return True
            except Exception as e:
                print(f"S3 write error for {filename}: {e}")
                # Fall back to local if S3 fails
                if local_path:
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'w') as f:
                        f.write(json_content)
                return False
        else:
            # Local storage
            if local_path:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'w') as f:
                    f.write(json_content)
            return True

    def is_using_s3(self):
        """Check if S3 storage is active"""
        return self._use_s3


# Global instance
_storage = None


def get_storage(bucket_name=None, region_name=None):
    """
    Get or create the global S3Storage instance

    Args:
        bucket_name: S3 bucket name (optional, uses env var if not provided)
        region_name: AWS region (optional)

    Returns:
        S3Storage instance
    """
    global _storage
    if _storage is None:
        _storage = S3Storage(bucket_name, region_name)
    return _storage


def init_storage(bucket_name=None, region_name=None):
    """
    Initialize storage with specific settings (call at app startup)

    Args:
        bucket_name: S3 bucket name
        region_name: AWS region
    """
    global _storage
    _storage = S3Storage(bucket_name, region_name)
    return _storage
