import os
import shutil
import random
import re
from collections import defaultdict

categories = ['ani', 'arc', 'cha']

def sample_authentic_for_prompt(
        input_dir = "CASIA2/Au_sample", output_dir = "CASIA2/Au_additional", total_samples = 38):

    os.makedirs(output_dir, exist_ok=True)

    # Group files by category
    category_files = defaultdict(list)
    pattern = re.compile(r"^Au_(\w+)_\d+\.(jpg|jpeg|png)$", re.IGNORECASE)

    for filename in os.listdir(input_dir):
        match = pattern.match(filename)
        if match:
            category = match.group(1).lower()
            if category in categories:
                category_files[category].append(filename)

    # Determine how many to sample per category
    base_count = total_samples // len(categories)
    remainder = total_samples % len(categories)

    samples_per_category = {cat: base_count for cat in categories}
    for i, cat in enumerate(categories[:remainder]):
        samples_per_category[cat] += 1

    selected_files = []

    for cat in categories:
        files = category_files[cat]
        if len(files) < samples_per_category[cat]:
            raise ValueError(f"Not enough files in category '{cat}' to sample {samples_per_category[cat]}")
        selected = random.sample(files, samples_per_category[cat])
        selected_files.extend(selected)

    # Move selected files to new directory
    for filename in selected_files:
        src_path = os.path.join(input_dir, filename)
        dst_path = os.path.join(output_dir, filename)
        shutil.move(src_path, dst_path)

    print(f"Moved {len(selected_files)} images to {output_dir}")


def sample_spliced_for_prompt(
    input_dir = "CASIA2/Sp_sample", output_dir = "CASIA2/Sp_additional", total_samples = 50):
    os.makedirs(output_dir, exist_ok=True)

    # Regex to extract source and destination categories
    pattern = re.compile(r"^Tp_D_[^_]+_[^_]+_[^_]+_([a-zA-Z]+)\d+_([a-zA-Z]+)\d+_\d+\.(jpg|jpeg|png)$", re.IGNORECASE)

    # Group files by category pair (src, dst)
    combo_bins = defaultdict(list)
    for filename in os.listdir(input_dir):
        match = pattern.match(filename)
        if match:
            src_cat = match.group(1).lower()
            dst_cat = match.group(2).lower()
            if src_cat in categories and dst_cat in categories:
                combo_bins[(src_cat, dst_cat)].append(filename)

    # Category pairs and base allocation
    category_pairs = [(src, dst) for src in categories for dst in categories]
    base_count = total_samples // len(category_pairs)
    remainder = total_samples % len(category_pairs)

    allocation = {pair: base_count for pair in category_pairs}
    for i in range(remainder):
        allocation[category_pairs[i]] += 1

    selected_files = []
    deficit = 0
    excess_pool = []

    # First pass: try to satisfy allocation from bins
    for pair in category_pairs:
        files = combo_bins.get(pair, [])
        need = allocation[pair]
        if len(files) >= need:
            sampled = random.sample(files, need)
        else:
            sampled = files  # take all available
            deficit += need - len(files)
        selected_files.extend(sampled)

        # Track leftover files from bins with extra
        remaining = list(set(files) - set(sampled))
        if remaining:
            excess_pool.extend(remaining)

    # Second pass: fill deficit from excess pool
    if deficit > 0:
        if len(excess_pool) < deficit:
            raise ValueError(
                f"Unable to meet total sample requirement. Deficit of {deficit} but only {len(excess_pool)} extras available.")
        supplement = random.sample(excess_pool, deficit)
        selected_files.extend(supplement)

    # Move selected files
    for filename in selected_files:
        src = os.path.join(input_dir, filename)
        dst = os.path.join(output_dir, filename)
        shutil.move(src, dst)

    print(f"Moved {len(selected_files)} spliced images to {output_dir}")


def main():
    # sample_authentic_for_prompt()
    sample_spliced_for_prompt()

if __name__ == "__main__":
    main()