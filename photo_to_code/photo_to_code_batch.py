import argparse
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

import base64
from glob import glob


def load_api_key():
    """
    Load the OpenAI API key from the .env file.
    Raises ValueError if the key is not found.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    return api_key


client = OpenAI(api_key=load_api_key())

def encode_image(image_path):
    """
    Encode image to base64 format.

    Args:
        image_path (str): The file path to the image to encode.

    Returns:
        str: The base64 encoded string of the image.
    """
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return encoded

def extract_code_from_image(image_path, model="gpt-4o"):
    """
    Extract Python code from an image using OpenAI's model.

    Args:
        image_path (str): The file path to the image containing Python code.
    
    Returns:
        str: The extracted Python code.
    """
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(model=model,
    messages=[
        {
            "role": "system",
            "content": "You are an expert OCR and Python code extraction assistant. Extract only the Python code from the image provided. Do not add explanations."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    max_tokens=4096)

    code = response.choices[0].message.content
    return code

def save_code_to_file(code, output_path):
    """
    Save the extracted code to a file.

    Args:
        code (str): The Python code to save.
        output_path (str): The file path where the code should be saved.
    """
    with open(output_path, "w") as f:
        f.write(code)
    print(f"✅ Saved to {output_path}")

def process_folder(folder_path):
    """
    Process a folder of images and extract Python code from each.

    Args:
        folder_path (str): The path to the folder containing image files.
    """
    image_files = sorted(glob(os.path.join(folder_path, "IMG_*.JPG")))

    if not image_files:
        print("❌ No matching files found.")
        return

    for image_path in image_files:
        filename = os.path.basename(image_path)
        match = re.match(r"IMG_(\d+)\.JPG", filename, re.IGNORECASE)
        if not match:
            print(f"⚠ Skipping file with unexpected name format: {filename}")
            continue

        number = match.group(1)
        output_filename = f"script_{number}.py"

        try:
            code = extract_code_from_image(image_path)
            save_code_to_file(code, output_filename)
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

def main():
    """
    Main entry point of the script.
    Sets up argument parsing and initiates the processing of images.
    """
    parser = argparse.ArgumentParser(description="Batch convert photos of Python code into text using OpenAI Vision.")
    parser.add_argument("--folder", default="photos", help="Folder containing image files (default: photos/)")

    args = parser.parse_args()

    load_api_key()
    process_folder(args.folder)


if __name__ == "__main__":
    main()