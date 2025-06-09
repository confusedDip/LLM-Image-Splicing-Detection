# Image Splicing Detection using GPT-4V

This repository accompanies the paper:  
**“Spliced, or Not Spliced, That Is the Question”: Can ChatGPT Perform Image Splicing Detection? A Preliminary Study**  
Authored by [Souradip Nath (@confusedDip)](https://github.com/confusedDip)

This project investigates the capabilities of GPT-4V in detecting image splicing without any task-specific training. The repository contains code for dataset preparation, multimodal prompting strategies, and performance analysis as described in the paper.

### Repository Structure

#### 📁 Dataset Preparation
- `download.py`  
  Script to download the CASIA v2.0 dataset from Kaggle.
  
- `sampling.py`  
  Prepares the evaluation subset of the dataset following the protocol outlined in the paper.

- `additional_sampling.py`  
  Samples additional images used as in-context examples for few-shot and chain-of-thought prompting strategies.

#### 🤖 LLM-Based Splicing Detection
- `zeroshot.py`  
  Performs detection using **Zero-Shot Prompting**, where the model receives only task instructions without examples.

- `fewshot.py`  
  Implements **Few-Shot Prompting**, where the model is guided using labeled in-context examples.

- `fewshotCoT.py`  
  Employs **Few-Shot Chain-of-Thought Prompting**, where each example includes step-by-step reasoning for improved interpretability.

#### 📊 Performance Evaluation
- `analysis_au.py`  
  Evaluates detection performance for **authentic** image samples.

- `analysis_sp.py`  
  Evaluates detection performance for **spliced** image samples.

### Citation

If you find this work useful, please consider citing our paper.

```
@misc{nath2025chatgptperformimagesplicing,
      title={{“Spliced, or not spliced, that is the question”: Can ChatGPT Perform Image Splicing Detection? A Preliminary Study}}, 
      author={Souradip Nath},
      year={2025},
      eprint={2506.05358},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2506.05358}, 
}
```
