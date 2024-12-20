from datetime import datetime
import subprocess
import time
import boto3
import os

# captures an image every X seconds and uploads it to AWS storage bucket


# aws s3 setup
BUCKET_NAME = 'grobot-data-bucket'
s3_client = boto3.client('s3')
S3_FOLDER = 'microgreen-images/'

IMAGE_FOLDER = '/home/raspberrypi/Desktop/grobot/' 

def capture_image():
#     capture image with rpicam
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    image_path = f'{IMAGE_FOLDER}photo_{timestamp}.jpg'
    try:
        subprocess.run(
            ['rpicam-jpeg', '-o', image_path, '-n'],
            )
        return image_path
    except subprocess.CalledProcessError as e:
        print(f'Error capturing image: {e}')
        return None

def upload_to_s3(file_path):
#     upload a file to s3
    try:
        file_name = os.path.basename(file_path)
        s3_client.upload_file(file_path, BUCKET_NAME, f'{S3_FOLDER}{file_name}')
        print(f'Uploaded {file_name} to S3')
    except Exception as e:
        print(f'Error uploading to S3: {e}')

def main():
    while True:
        image_path = capture_image()
        if image_path:
            upload_to_s3(image_path)
#             clean up local image
            os.remove(image_path) 
        time.sleep(60)
        
if __name__ == '__main__':
    main()