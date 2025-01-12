from datetime import datetime
import subprocess
import time
import boto3
import os
import RPi.GPIO as GPIO

# turns on the watering system every X seconds, then captures an image and uploads it to AWS storage bucket


# aws s3 setup
BUCKET_NAME = 'grobot-data-bucket'
s3_client = boto3.client('s3')
S3_FOLDER = 'microgreen-images/'
IMAGE_FOLDER = '/home/raspberrypi/Desktop/grobot/'

# compressore relay setup
RELAY_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

TIME_BETWEEN = 120 # seconds to wait between watering/image capture
WATERING_TIME = 60 # seconds to turn on misting system

# -----------MISTING SYSTEM FNS-----------
def water():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(WATERING_TIME)
    GPIO.output(RELAY_PIN, GPIO.LOW)

# ----------GROWTH IMAGE FNS--------------
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
#         TURN ON MISTING SYSTEM
        water()
#         CAPTURE AND UPLOAD GROWTH IMAGE
        image_path = capture_image()
        if image_path:
#             upload_to_s3(image_path)
# ^ above line temporarily commented out so not using free aws limits while testing growing
#             clean up local image
            os.remove(image_path) 
        time.sleep(TIME_BETWEEN)
        
if __name__ == '__main__':
    main()