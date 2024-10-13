import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen import File as MutagenFile
import ffmpeg

def get_file_type(file_path):
    _, ext = os.path.splitext(file_path.lower())
    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
        return 'image'
    elif ext in ['.mp3', '.wav', '.flac']:
        return 'audio'
    elif ext in ['.mp4', '.avi', '.mov']:
        return 'video'
    else:
        return 'unknown'

def delete_image_metadata(file_path, categories=None):
    with Image.open(file_path) as img:
        # Remove all EXIF data
        data = img.getexif()
        if categories:
            for category in categories:
                if category in data:
                    del data[category]
        else:
            data.clear()
        
        # Remove ICC profile
        img.info.pop('icc_profile', None)
        
        # Create a new image without metadata
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(list(img.getdata()))
        
        # Save the new image without metadata
        new_img.save(file_path, format=img.format)

def delete_audio_metadata(file_path, categories=None):
    audio = MutagenFile(file_path)
    if categories:
        for category in categories:
            if category in audio:
                del audio[category]
    else:
        audio.clear()
    audio.save()

def delete_video_metadata(file_path):
    output_file = file_path + ".temp"
    stream = ffmpeg.input(file_path)
    stream = ffmpeg.output(stream, output_file, map_metadata=-1)
    ffmpeg.run(stream, overwrite_output=True)
    os.replace(output_file, file_path)

def add_basic_metadata(file_path, file_type):
    if file_type == 'image':
        with Image.open(file_path) as img:
            width, height = img.size
            return f"Size: {width}x{height}, Type: {img.format}"
    elif file_type == 'audio':
        audio = MutagenFile(file_path)
        return f"Format: {audio.info.pprint()}"
    elif file_type == 'video':
        probe = ffmpeg.probe(file_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream:
            width = video_stream['width']
            height = video_stream['height']
            return f"Resolution: {width}x{height}"
    return "No basic metadata available"

def add_artist_metadata(file_path, file_type, artist):
    if file_type == 'image':
        with Image.open(file_path) as img:
            exif = img.getexif()
            artist_tag = next((tag for tag, name in TAGS.items() if name == 'Artist'), None)
            if artist_tag:
                exif[artist_tag] = artist
                img.save(file_path, exif=exif)
            else:
                print("Warning: Couldn't add artist metadata to image.")
    elif file_type in ['audio', 'video']:
        try:
            audio = MutagenFile(file_path)
            audio['artist'] = artist
            audio.save()
        except Exception as e:
            print(f"Warning: Couldn't add artist metadata to {file_type} file. Error: {str(e)}")

def main():
    while True:
        path = input("Enter the path to the folder/file (or 'q' to quit): ")
        if path.lower() == 'q':
            break

        if os.path.isfile(path):
            files = [path]
        elif os.path.isdir(path):
            files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        else:
            print("Invalid path. Please try again.")
            continue

        for file_path in files:
            file_type = get_file_type(file_path)
            if file_type == 'unknown':
                print(f"Skipping unsupported file: {file_path}")
                continue

            print(f"Processing {file_path}")
            delete_all = input("Delete all metadata? (y/n): ").lower() == 'y'

            if delete_all:
                if file_type == 'image':
                    delete_image_metadata(file_path)
                elif file_type == 'audio':
                    delete_audio_metadata(file_path)
                elif file_type == 'video':
                    delete_video_metadata(file_path)

                refill = input("Re-fill basic information? (y/n): ").lower() == 'y'
                if refill:
                    basic_info = add_basic_metadata(file_path, file_type)
                    print(f"Added basic metadata: {basic_info}")

            else:
                if file_type in ['image', 'audio']:
                    categories = input("Enter metadata categories to delete (comma-separated): ").split(',')
                    if file_type == 'image':
                        delete_image_metadata(file_path, categories)
                    else:
                        delete_audio_metadata(file_path, categories)
                else:
                    print("Selective metadata deletion not supported for video. Deleting all metadata.")
                    delete_video_metadata(file_path)

            artist = input("Enter artist metadata: ")
            add_artist_metadata(file_path, file_type, artist)

            print(f"Processed {file_path}")

        print("All files in the path have been processed.")

if __name__ == "__main__":
    main()