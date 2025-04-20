# Counting-with-Perspective-and-CoT-in-Videos
Using Perspectives and Chain-of-Thought to help Gemini count Object Instances in Videos from Continuous Perception Benchmark
Based on https://github.com/shaunak27/video_instance_counting.git

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
