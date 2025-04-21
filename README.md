# Counting-with-Perspective-and-CoT-in-Videos
Using Perspectives and Chain-of-Thought to help Gemini count Object Instances in Videos from Continuous Perception Benchmark
Based on https://github.com/shaunak27/video_instance_counting.git

## Key Findings

In improving Gemini's counting performance, I uncovered 2 key reasons for its failure   
### Camera Motion Misinterpretation:  
Given a camera strictly moving rightward:  
1. Problem: Gemini thought the camera went rightwards then reversed leftwards  
2. Impact: Gemini explains the second half of the video are the same object instances seen in first half  
3. **Perspective** Fix: Adding in the prompt that the camera moves strictly rightwards corrected counting from 12 to 24  
### Bias towards multiplication:  
Given videos with cakes on tables  
1. Problem: Gemini assumes same number of cakes on all tables
2. Impact: Gemini multiplies number of cakes on a table by number of tables  
3. **TbTCoT** Fix: Force Gemini to count number of cakes Table by Table with Chain-of-Thought (TbTCoT)

   

| Model             | Prompt Type          | Off-by-zero (%) | Off-by-one (%) | Off-by-five (%) |
|-------------------|----------------------|----------|-----|------|
| Gemini 1.5 Flash  | original             | 10        | 24   | 57    |
|                   | perspective          | 13.5        | 28   | 57.5    |
|                   | TbTCoT             | 8        | 25   | 80    |
|                   | Combined | 10        | 27   | 76.5    |
| Gemini 2.0 Flash  | original             | 8        | 21   | 58     |
|                   | perspective          | 8.5        | 24.5   | 60.5    |

### Perspectives with Gemini 2.5 Flash
Given a strictly rightwards motion of camera:
1. **54%** of the data was predicted to have changes in yaw (i.e. panning)
2. **52%** of the data was predicted to have forward or backward camera movement
3. 91.5% of the data was predicted to have side-to-side movement (correct)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/robertocarlosjuan/Counting-with-Perspective-and-CoT-in-Videos.git
    ```
2. Navigate to the project directory:
    ```sh
    cd Counting-with-Perspective-and-CoT-in-Videos
    ```
3. Install the required dependencies:
    Ideally you should create a virtual environment with Python 3.10. Install the Google Generative AI library to access Gemini.
    ```sh
    pip install google-generativeai
    pip install git+https://github.com/huggingface/transformers@21fac7abba2a37fae86106f87fcf9974fd1e3830 accelerate
    pip install qwen-vl-utils[decord]
    pip install bitsandbytes
    pip install flash-attn --no-build-isolation
    ```
4. Set up API keys for [Gemini](https://ai.google.dev) for your account. Set up the API key in the environment variable `GEMINI_API_KEY` as shown below:
    ```sh
    export GEMINI_API_KEY=your_api_key
    ```
## Evaluation

1. Download the data from the [Google Drive link](https://drive.google.com/drive/u/2/folders/1gvX3JOXd06CMdCSMJGhwoCgWs5wK-nXb).
2. Run the evaluation script:
    ```sh
    python evaluation.py --data_path /path/to/your/data --ground_truth_path /path/to/your/ground_truth_file --output_file /path/to/output --prompt_type [original|perspective|one_shot|one_shot_perspective] --model [gemini|qwen]
    ```
3. To assess perspective
    ```sh
    python evaluation.py --data_path data --ground_truth_path ground_truth --output_folder results --prompt_type structured_perspective --model "gemini-2.5.pro-exp-03-25"
    ```
