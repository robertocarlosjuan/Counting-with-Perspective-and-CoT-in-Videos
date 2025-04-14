# Counting-with-Perspective-and-CoT-in-Videos
Using Perspectives and Chain-of-Thought to help Gemini count Object Instances in Videos from Continuous Perception Benchmark
Based on https://github.com/shaunak27/video_instance_counting.git

## Key Findings
1. Gemini is biased to multiplying: Assumes every table has same number of objects.  
   -> Force it to count for each table  
   -> Reprompting as Table-by-table Chain-of-Though (TbTCoT) model  
2. Gemini has no idea how the camera is moving.  
   -> It thinks it's zooming out or sth when its just left to right movement  
   -> Reprompting as Perspective model  

| Models | Prompt       | Off-by-zero (%) | Off-by-one (%) | Off-by-five (%) |
|--------|--------------|------------------|----------------|-----------------|
| Gemini1.5-flash | Original     | 10               | 24             | 57              |
|        | Perspective  | 13.5             | 28             | 57.5            |
|        | TbTCoT       | 8                | 25             | 80              |

## Further Insights with Gemini 2.0
`prompt = 'As a proficient video understanding model, your task is to describe the camera perspective in the video and provide a detailed description that includes aspects such as the camera's angle, movement, framing, zoom level, and depth of field.'`
From the prompt above, for this dataset consisting of only left to right dolly movement:  
90% is determined to be a panning movement  
4.2% determines some zoom level changes
5.6% correctly identifies only a dolly movement

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

1. Download the data from the [Google Drive link](https://drive.google.com/drive/u/2/folders/1gvX3JOXd06CMdCSMJGhwoCgWs5wK-nXb) and [example video](https://drive.google.com/file/d/1DLP4FCWokGS6uKz98FD4e1Snh0LQ24W1/view?usp=sharing).
2. Run the evaluation script:
    ```sh
    python evaluation.py --data_path /path/to/your/data --ground_truth_path /path/to/your/ground_truth_file --output_file /path/to/output --prompt_type [original|perspective|one_shot|one_shot_perspective] --model [gemini|qwen]
    ```
