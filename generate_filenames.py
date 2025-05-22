import os

def main():
    # Define the base directory and subdirectories
    base_dir = 'CASIA2'
    subdirs = ['Au_additional', 'Au_sample', 'Sp_additional', 'Sp_sample']

    # Function to collect filenames and write to corresponding text files
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        output_file_path = os.path.join(base_dir, f'{subdir}.txt')

        if os.path.exists(dir_path):
            with open(output_file_path, 'w') as f_out:
                for filename in os.listdir(dir_path):
                    if os.path.isfile(os.path.join(dir_path, filename)):
                        f_out.write(f"{filename}\n")

    output_file_paths = [os.path.join(base_dir, f'{subdir}.txt') for subdir in subdirs]

if __name__=="__main__":
    main()