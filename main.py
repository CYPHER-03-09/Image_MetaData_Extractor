import os
import requests
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO
from datetime import datetime


def extract_image_info(image_path, desired_tags):
    try:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            if response.status_code != 200:
                print(f"Error fetching image from {image_path}")
                return {}
            image = Image.open(BytesIO(response.content))
            file_modify_date = response.headers.get('Last-Modified', 'No Last-Modified header')
            if file_modify_date != 'No Last-Modified header':
                file_modify_date = datetime.strptime(file_modify_date, '%a, %d %b %Y %H:%M:%S %Z')
            file_info = {
                "FileName": image_path.split("/")[-1],
                "FileSize": round(len(response.content) / (1024 * 1024), 2),  # File size in MB
                "FileType": image.format.lower(),
                "ImageSize": image.size,
                "FileModifyDate": file_modify_date
            }
        else:
            # If it's a local file, get basic file info
            file_size_bytes = os.path.getsize(image_path)
            file_modify_time = os.path.getmtime(image_path)
            file_modify_date = datetime.fromtimestamp(file_modify_time)
            file_info = {
                "FileName": os.path.basename(image_path),
                "FileSize": round(file_size_bytes/(1024 * 1024), 2),
                "FileType": os.path.splitext(image_path)[1].lower(),
                "FileModifyDate": file_modify_date
            }
            image = Image.open(image_path)
            file_info["ImageSize"] = image.size

        # Check if the image format supports Exif data
        if image.format != 'JPEG' and image.format != 'TIFF':
            print(f"Image format '{image.format}' does not support Exif data.")
            return file_info

        # Get Exif data
        exif_data = image.getexif()
        if not exif_data:
            print(f"No Exif data found in image: {image_path}")
            return file_info

        # Extract specified Exif tags
        extracted_data = {}
        for tag_id in exif_data:
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name in desired_tags:
                data = exif_data.get(tag_id)
                if isinstance(data, bytes):
                    data = "Binary Data"
                extracted_data[tag_name] = data

        # Add extracted Exif data to the file info
        file_info.update(extracted_data)

        return file_info

    except IOError:
        print(f"Error opening image file: {image_path}")
        return {}
#main
'''You can add image path from from local computer/files or from any valid url and if you want to 
extract other tags from the image you just have to add tags in desired tags like - 
desired_tags = ["DateTime", "GPSInfo", "ResolutionUnit", "ExifOffset", "ImageDescription", 
                "XResolution", "YResolution", "YCbCrPositioning", "Orientation"] '''
image_path = "https://upload.wikimedia.org/wikipedia/commons/3/38/JPEG_example_JPG_RIP_001.jpg"
desired_tags = ["DateTime"]
image_info = extract_image_info(image_path, desired_tags)
if image_info:
    for key, value in image_info.items():
        print(f"{key}: {value}")
else:
    print("No data found or extracted from the image.")
