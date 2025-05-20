import pandas as pd

def analyze():
    # Load the splicing result CSV
    file_path = "Sp_sample_llm_decisions_zero_shot.csv"
    df = pd.read_csv(file_path)

    # Normalize decision labels
    df['LLM-decision'] = df['LLM-decision'].str.strip().str.lower()

    # Calculate total counts
    total_authentic = (df['LLM-decision'] == 'authentic').sum()
    total_spliced = (df['LLM-decision'] == 'spliced').sum()
    overall_accuracy = total_spliced / (total_authentic + total_spliced) * 100

    print(f""
          f"Total #Authentic = {total_authentic}, "
          f"Total Spliced = {total_spliced},"
          f"Accuracy = {overall_accuracy}%")

    # Define the categories of interest
    categories = ['ani', 'arc', 'cha']

    # Create a new column indicating group membership (can belong to multiple groups)
    group_stats = []

    for category in categories:
        # Filter rows where the category appears in either source or destination
        mask = df['filename'].str.contains(fr'_{category}\d+', case=False, regex=True)
        subset = df[mask]

        # Count authentic and spliced
        authentic = (subset['LLM-decision'] == 'authentic').sum()
        spliced = (subset['LLM-decision'] == 'spliced').sum()
        accuracy = spliced / (authentic + spliced) * 100 if (authentic + spliced) > 0 else 0

        group_stats.append({
            'category_group': category,
            'Total Authentic': authentic,
            'Total Spliced': spliced,
            'Accuracy (%)': round(accuracy, 2)
        })

    print(group_stats)


    overall_stats = {
        'Total Authentic': total_authentic,
        'Total Spliced': total_spliced,
        'Overall Accuracy': round(overall_accuracy, 4)
    }

    print(overall_stats)

if __name__=="__main__":
    analyze()