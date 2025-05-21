import pandas as pd

def analyze():
    # Load the CSV file
    file_path = "results/Au_sample_llm_decisions_fewshot_with_cot.csv"
    df = pd.read_csv(file_path)

    # Normalize and parse decisions
    df['LLM-decision'] = df['LLM-decision'].str.strip().str.lower()

    # Extract category from filename (assumes format like Au_arc_XXXXX.jpg)
    df['category'] = df['filename'].str.extract(r'Au_(\w+)_\d+')

    # Global stats
    total_authentic = (df['LLM-decision'] == 'authentic').sum()
    total_spliced = (df['LLM-decision'] == 'spliced').sum()
    overall_accuracy = total_authentic / (total_authentic + total_spliced) * 100

    print(f""
          f"Total #Authentic = {total_authentic}, "
          f"Total Spliced = {total_spliced},"
          f"Accuracy = {overall_accuracy}%")

    # Per-category stats
    category_stats = (
        df.groupby('category')['LLM-decision']
        .value_counts()
        .unstack(fill_value=0)
        .assign(accuracy=lambda x: x.get('authentic', 0) / (x.get('authentic', 0) + x.get('spliced', 0)))
    )

    # import ace_tools as tools; tools.display_dataframe_to_user(name="Per-category Statistics", dataframe=category_stats)

    # overall_stats = {
    #     'Total Authentic': total_authentic,
    #     'Total Spliced': total_spliced,
    #     'Overall Accuracy': round(overall_accuracy, 4)
    # }

    print(category_stats)

if __name__ == "__main__":
    analyze()
