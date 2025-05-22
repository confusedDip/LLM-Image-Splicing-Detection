"""
Sampling datasets from the original CASIA v2.0 dataset
"""
import os
import shutil
from collections import Counter
import re

# Configuration
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')

def sample_authentic(input_dir="CASIA2/Au", output_dir='CASIA2/Au_sample'):

    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Gather all files and extract categories
    category_counter = Counter()
    file_map = {}

    pattern = re.compile(r"^Au_(\w+)_\d+\.(?:jpg|jpeg|png)$", re.IGNORECASE)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(VALID_EXTENSIONS):
            match = pattern.match(filename)
            if match:
                category = match.group(1)
                category_counter[category] += 1
                file_map.setdefault(category, []).append(filename)

    # Step 2: Identify top 5 categories
    top_categories = [cat for cat, _ in category_counter.most_common(3)]
    print(f"The top 3 categories are: {top_categories}")

    # Step 3: Copy files from top categories
    for category in top_categories:
        for file in file_map[category]:
            src = os.path.join(input_dir, file)
            dst = os.path.join(output_dir, file)
            shutil.copy2(src, dst)

    print("Sampling complete. Files copied to:", output_dir)

    return top_categories

def sample_spliced(input_dir="CASIA2/Tp", output_dir='CASIA2/Sp_sample', categories=None):
    if categories is None or not categories:
        raise ValueError("You must provide a list of top categories.")

    os.makedirs(output_dir, exist_ok=True)

    # Pattern: Tp_<D|S>_XXX_X_X_<src_category><id>_<dst_category><id>_<id>.ext
    pattern = re.compile(
        r"^Tp_D_[^_]+_[^_]+_[^_]+_([a-zA-Z]+)\d+_([a-zA-Z]+)\d+_\d+\.(jpg|jpeg|png)$",
        re.IGNORECASE
    )

    matched_files = []

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(VALID_EXTENSIONS):
            match = pattern.match(filename)
            if match:
                src_cat, dst_cat = match.group(1).lower(), match.group(2).lower()
                if src_cat in categories or dst_cat in categories:
                    matched_files.append(filename)
                    shutil.copy2(os.path.join(input_dir, filename), os.path.join(output_dir, filename))

    print(f"Sampled {len(matched_files)} tampered (spliced) images to {output_dir}")


def main():
    top_categories = sample_authentic()
    sample_spliced(categories=top_categories)

if __name__ == "__main__":
    main()