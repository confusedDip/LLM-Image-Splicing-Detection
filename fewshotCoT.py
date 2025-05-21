import base64
import csv
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load the OpenAI API key
load_dotenv()
client = OpenAI()

def get_all_image_paths(folder):
    valid_extensions = ('.jpg', '.jpeg', '.png')
    return [
        os.path.join(folder, fname)
        for fname in sorted(os.listdir(folder))
        if fname.lower().endswith(valid_extensions)
    ]

def get_all_text_paths(folder):
    return [
        os.path.join(folder, fname)
        for fname in sorted(os.listdir(folder))
        if fname.lower().endswith('.txt')
    ]

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_category_from_filename(filename):
    if 'ani' in filename:
        return 'ani'
    elif 'arc' in filename:
        return 'arc'
    elif 'cha' in filename:
        return 'cha'
    else:
        return None

def match_cot_examples(category, cot_dir, img_dir):
    cot_files = [f for f in os.listdir(cot_dir) if f.endswith('.txt') and category in f]
    # sampled_cots = random.sample(cot_files, min(2, len(cot_files)))
    cot_examples = []

    for cot_file in cot_files:
        image_name = cot_file.replace('.txt', '.jpg')
        image_path = os.path.join(img_dir, image_name)
        cot_path = os.path.join(cot_dir, cot_file)

        if os.path.exists(image_path):
            with open(cot_path, 'r') as f:
                reasoning = f.read().strip()
            cot_examples.append((image_path, reasoning))
    return cot_examples

def generate_few_shot_prompt_with_cot(auth_examples, spliced_examples):
    messages = []

    for img_path, reasoning in auth_examples:
        base64_img = encode_image_to_base64(img_path)
        messages.append({"type": "text", "text": f"For example, this image is Authentic. {reasoning}"})
        messages.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}})

    for img_path, reasoning in spliced_examples:
        base64_img = encode_image_to_base64(img_path)
        messages.append({"type": "text", "text": f"For example, this image is Spliced. {reasoning}"})
        messages.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}})

    messages.append({"type": "text", "text":
        "Inspect the following image and identify whether it is original or has been spliced. "
        "Only Answer with 'Authentic' for an unedited image, or 'Spliced' for a manipulated one. "
        # "Provide brief reasoning if needed."
    })

    return messages

def send_image_to_openai_with_fewshot(image_path, au_examples, sp_examples):
    messages = generate_few_shot_prompt_with_cot(au_examples, sp_examples)

    base64_image = encode_image_to_base64(image_path)
    messages.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[{"role": "user", "content": messages}],
        temperature=0,
        max_tokens=300
    )
    result = response.choices[0].message.content.strip()
    print(result)
    return result

def main():
    folder = "CASIA2/Au_sample"
    output_csv = "results/Au_sample_llm_decisions_fewshot_with_cot.csv"

    image_paths = get_all_image_paths(folder)

    # random.seed(42)
    au_img_dir = "CASIA2/Au_additional"
    sp_img_dir = "CASIA2/Sp_additional"
    au_cot_dir = "CASIA2/Au_CoT"
    sp_cot_dir = "CASIA2/Sp_CoT"

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    with open(output_csv, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "LLM-decision"])

        for path in image_paths:
            try:
                print(f"Processing {path}...")
                category = extract_category_from_filename(os.path.basename(path))
                au_examples = match_cot_examples(category, au_cot_dir, au_img_dir)
                sp_examples = match_cot_examples(category, sp_cot_dir, sp_img_dir)
                # print(au_examples, sp_examples)
                decision = send_image_to_openai_with_fewshot(path, au_examples, sp_examples)
                writer.writerow([os.path.basename(path), decision])
            except Exception as e:
                print(f"Error processing {path}: {e}")
                writer.writerow([os.path.basename(path), f"ERROR: {e}"])

    print(f"\nProcessing complete. Results saved to: {output_csv}")

if __name__ == "__main__":
    main()
