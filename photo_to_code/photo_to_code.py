import argparse
import os
from dotenv import load_dotenv
import openai
import base64

def load_api_key():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    openai.api_key = api_key

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return encoded

def extract_code_from_image(image_path, model="gpt-4o"):
    base64_image = encode_image(image_path)

    response = openai.ChatCompletion.create(
        model=model,
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
        max_tokens=4096
    )

    code = response.choices[0].message.content
    return code

def save_code_to_file(code, output_path):
    with open(output_path, "w") as f:
        f.write(code)
    print(f"✅ Code saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert photo of Python code into text using OpenAI Vision.")
    parser.add_argument("image_path", help="Path to the image file containing Python code")
    parser.add_argument("output_path", help="Path to save the extracted Python code")

    args = parser.parse_args()

    load_api_key()
    code = extract_code_from_image(args.image_path)
    save_code_to_file(code, args.output_path)

if __name__ == "__main__":
    main()

