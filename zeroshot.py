import os
import csv
import base64
from dotenv import load_dotenv
from openai import OpenAI

# Load the OpenAI API key
load_dotenv()
client = OpenAI()

def get_all_image_paths(folder="Au_sample"):
    """Return all image file paths in the folder with valid extensions."""
    valid_extensions = ('.jpg', '.jpeg', '.png')
    return [
        os.path.join(folder, file_name)
        for file_name in sorted(os.listdir(folder))
        if file_name.lower().endswith(valid_extensions)
    ]

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_prompt():
    """Return the analysis prompt."""
    return ("Inspect the provided image and identify whether it is original or has been spliced. "
            "Answer with 'Authentic' for an unedited image, or 'Spliced' for a manipulated one.")

def send_image_to_openai(image_path):
    """Send an image to the OpenAI Vision model and get a response."""
    base64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": generate_prompt()
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0,           # For deterministic, reproducible results
        max_tokens=100
    )
    result = response.choices[0].message.content.strip()
    print(result)
    return result

def main():
    output_csv = "Au_sample_llm_decisions_zero_shot.csv"

    image_paths = get_all_image_paths()

    with open(output_csv, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "LLM-decision"])

        for path in image_paths:
            try:
                print(f"Processing {path}...")
                decision = send_image_to_openai(path)
                writer.writerow([os.path.basename(path), decision])
            except Exception as e:
                print(f"Error processing {path}: {e}")
                writer.writerow([os.path.basename(path), f"ERROR: {e}"])

    print(f"\nProcessing complete. Results saved to: {output_csv}")

if __name__ == "__main__":
    main()
