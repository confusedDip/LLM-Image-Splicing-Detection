import kagglehub

def download():
    # Download latest version of the CASIAv2.0 dataset
    path = kagglehub.dataset_download("divg07/casia-20-image-tampering-detection-dataset")
    print("Path to dataset files:", path)

def main():
    download()

if __name__ == "__main__":
    main()