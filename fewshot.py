import os
import csv
import base64
import random
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load the OpenAI API key
load_dotenv()
client = OpenAI()

def get_all_image_paths(folder):
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

def extract_category_from_filename(filename):
    """Extract category from authentic or spliced filename."""
    if 'ani' in filename:
        return 'ani'
    elif 'arc' in filename:
        return 'arc'
    elif 'cha' in filename:
        return 'cha'
    else:
        return None

def select_few_shot_examples(input_filename, au_pool, sp_pool):
    """Select 2 matching authentic and 2 matching spliced examples based on input image's category."""
    filename = os.path.basename(input_filename)
    category = extract_category_from_filename(filename)

    matching_au = []
    for p in au_pool:
        base = os.path.basename(p)
        if category in base:
            matching_au.append(p)

    matching_sp = []
    for p in sp_pool:
        base = os.path.basename(p)
        if category in base:
            matching_sp.append(p)

    random.seed(42)
    # Fallback if not enough relevant examples
    sampled_au = random.sample(matching_au, min(2, len(matching_au))) if matching_au else random.sample(au_pool, 2)
    sampled_sp = random.sample(matching_sp, min(2, len(matching_sp))) if matching_sp else random.sample(sp_pool, 2)

    return sampled_au, sampled_sp

def generate_few_shot_prompt(auth_paths, splice_paths):
    """Return few-shot image-text pairs for the system prompt."""
    messages = []

    for path in auth_paths:
        base64_img = encode_image_to_base64(path)
        messages.append({"type": "text", "text": "For example, this image is Authentic."})
        messages.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })

    for path in splice_paths:
        base64_img = encode_image_to_base64(path)
        messages.append({"type": "text", "text": "For example, this image is Spliced."})
        messages.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })

    # Final task prompt with reasoning instruction
    messages.append({"type": "text", "text":
        "Inspect the following image and identify whether it is original or has been spliced. "
        "Answer with 'Authentic' for an unedited image, or 'Spliced' for a manipulated one. "
        # "If the answer is not obvious, provide a brief explanation for your decision."
    })

    return messages

def send_image_to_openai_with_fewshot(image_path, au_examples, sp_examples):
    """Send the target image with few-shot examples to the model."""
    few_shot_messages = generate_few_shot_prompt(au_examples, sp_examples)

    base64_image = encode_image_to_base64(image_path)
    few_shot_messages.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
    })

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",  # Vision-capable model
        messages=[{"role": "user", "content": few_shot_messages}],
        temperature=0,
        max_tokens=150
    )
    result = response.choices[0].message.content.strip()
    print(result)
    return result

def main():
    folder = "CASIA2/Sp_sample"
    output_csv = "results/Sp_sample_llm_decisions_few_shot_run2.csv"

    image_paths = get_all_image_paths(folder)

    # Set seed for reproducibility
    random.seed(42)
    au_prompt_paths = get_all_image_paths("CASIA2/Au_additional")
    sp_prompt_paths = get_all_image_paths("CASIA2/Sp_additional")

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    with open(output_csv, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "LLM-decision"])

        for path in image_paths:
            try:
                print(f"Processing {path}...")
                au_examples, sp_examples = select_few_shot_examples(path, au_prompt_paths, sp_prompt_paths)
                decision = send_image_to_openai_with_fewshot(path, au_examples, sp_examples)
                writer.writerow([os.path.basename(path), decision])
            except Exception as e:
                print(f"Error processing {path}: {e}")
                writer.writerow([os.path.basename(path), f"ERROR: {e}"])

    print(f"\nProcessing complete. Results saved to: {output_csv}")

if __name__ == "__main__":
    main()
