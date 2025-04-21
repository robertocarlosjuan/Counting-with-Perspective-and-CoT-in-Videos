from qwen import QwenInference
import google.generativeai as genai
import os
import time
import json
from tqdm import tqdm
import argparse
import re
import dotenv
from perspective_utils import structured_perspective_generation_config, structured_perspective_prompt, clean_and_parse_camera_json
dotenv.load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"]) #

def get_video_input(video_file_name, chosen_model):
    if chosen_model == "qwen":
        return video_file_name
    elif "gemini" in chosen_model:
        try:
            video_file = genai.upload_file(path=video_file_name)
        except Exception as e:
            print(f"File upload error: {e}")
            return None

        try:
            while video_file.state.name == "PROCESSING":
                time.sleep(12)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                raise ValueError(video_file.state.name)
        except Exception as e:
            print(f"Error during file processing: {e}")
            return None
        return video_file
    else:
        print("Only implemented gemini and qwen")

def process_video(category, video, ground_truth_file,data_path,chosen_prompt="original", chosen_model="gemini-2.0-flash", qwen_inference=None, responses={}):

    if os.path.exists(video):
        video_file_name = video
    else:
        video_file_name = f"{data_path}/base_version/{category}/{video}"

        try:
            with open(ground_truth_file) as f:
                gt_file = json.load(f)
            gt_val = gt_file[f"{video.split('.')[0]}"]
        except Exception as e:
            print(f"Error reading ground truth file: {e}")
            return None, None

    input_options = {
        "original": [get_video_input(video_file_name, chosen_model), f"As a proficient video understanding model, your task is to closely observe the objects within the scene in the provided video and determine the total count of {category} present. Please provide your response as a single numerical value, indicating the quantity of {category} observed, without any other word."],
        "perspective": [get_video_input(video_file_name, chosen_model), f"In this video, the camera is moving in a straight line from the left side to the right side of the room. The camera is not panning or tilting, it is simply translating along a horizontal path.\nAs a proficient video understanding model, your task is to closely observe the objects within the scene in the provided video and determine the total count of {category}s present. Consider whether the {category}s are the same.\nPlease provide your response as a single numerical value, indicating the quantity of {category}s observed, without any other word.\n"],
        "one_shot": [f"### Task Description\nCount the number of {category}s on each table, starting from the first table to the last. After counting the {category}s on each table, calculate and provide the total number of {category}s across all tables.\n### Example:\n**Task**:", get_video_input('office1_cake_13_5cakes.mp4', chosen_model), "**Table Number** | **Number of {category}s**\n------- | --------\n1 | 3\n2 | 2\n**Total**:5 \n### New Task:\n**Task**:", get_video_input(video_file_name, chosen_model), "**Answer**: **Table Number** | **Number of {category}**\n------- | --------"],
        "one_shot_perspective":[f"### Task Description\nIn this video, the camera is moving in a straight line from the left side to the right side of the room. The camera is not panning or tilting, it is simply translating along a horizontal path.\nAs a proficient video understanding model, your task is to count the number of {category}s on each table, starting from the first table to the last. After counting the {category}s on each table, calculate and provide the total number of {category}s across all tables. Consider whether the {category}s are the same.\n### Example:\n**Task**:", get_video_input('office1_cake_13_5cakes.mp4', chosen_model), "**Table Number** | **Number of {category}s**\n------- | --------\n1 | 3\n2 | 2\n**Total**:5 \n### New Task:\n**Task**:", get_video_input(video_file_name, chosen_model), "**Answer**: **Table Number** | **Number of {category}**\n------- | --------"],
        "explain_perspective": [get_video_input(video_file_name, chosen_model), f"As a proficient video understanding model, your task is to describe the camera perspective in the video and provide a detailed description that includes aspects such as the camera's angle, movement, framing, zoom level, and depth of field."],
        "structured_perspective": [get_video_input(video_file_name, chosen_model), structured_perspective_prompt]
    }

    prompt = input_options[chosen_prompt] if chosen_prompt in input_options.keys() else chosen_prompt

    try:
        if "gemini" in chosen_model:
            model = genai.GenerativeModel(model_name=chosen_model)
            if chosen_prompt != "structured_perspective":
                response = model.generate_content(prompt, request_options={"timeout": 600}).text
            else:
                response = model.generate_content(
                    prompt, 
                    request_options={"timeout": 600},
                    generation_config=structured_perspective_generation_config
                    )
                response = json.loads(response.text)
        elif chosen_model == "qwen":
            response = qwen_inference.run(prompt)
        if chosen_prompt in ["original", "perspective", "one_shot", "one_shot_perspective"]:
            rsps = re.findall(r'\d+', response)[-1]
            rsps, gt_val = int(rsps), int(gt_val)
            responses[f"{video.split('.')[0]}"] = {"response": response, "rsps": rsps, "gt": gt_val}
            return rsps, gt_val
        else:
            responses[f"{video.split('.')[0]}"] = {"response": response}
            return None, None
    except Exception as e:
        print(f"Error during model generation: {e}")
        return None, None

def update_off_dict(off_dict, rsps, gt_val, video):
    if rsps == gt_val:
        off_dict['off_by_zero'].append(video)
    if abs(rsps - gt_val) <= 1:
        off_dict['off_by_one'].append(video)
    if abs(rsps - gt_val) <= 5:
        off_dict['off_by_five'].append(video)
    
    off_dict['total'] += 1
    return off_dict

def main():
    parser = argparse.ArgumentParser(description="Process videos and evaluate model performance.")
    parser.add_argument("--data_path", type=str, default="data", help="Path to the root data directory")
    parser.add_argument("--ground_truth_path", type=str, default="ground_truth", help="Path to the ground truth folder")
    parser.add_argument("--output_folder", type=str, default="results", help="Output file to save the results")
    parser.add_argument("--prompt_type", type=str, default="original", choices=["original", "perspective", "one_shot", "one_shot_perspective", "all", "explain_perspective", "structured_perspective"], help="type of prompt")
    parser.add_argument("--model", type=str, default="gemini-2.0-flash", help="model to use")
    args = parser.parse_args()
    output_file = os.path.join(args.output_folder, f"{args.model}_{args.prompt_type}.json")
    output_file_responses = os.path.join(args.output_folder, f"{args.model}_{args.prompt_type}_responses.json")
    if args.prompt_type == "all":
        args.prompt_options = ["original", "perspective", "one_shot", "one_shot_perspective"]
    else:
        args.prompt_options = [args.prompt_type]

    categories = os.listdir(os.path.join(args.data_path,"base_version"))
    qwen_inference = QwenInference() if args.model == "qwen" else None

    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            full_off_dict = json.load(f)
        with open(output_file_responses, "r") as f: 
            responses = json.load(f)
    else:
        full_off_dict = {'num':{}, 'video':{}}
        responses = {}
    for chosen_prompt in args.prompt_options:
        if chosen_prompt not in responses:
            responses[chosen_prompt] = {}
        print(chosen_prompt)
        if chosen_prompt in full_off_dict['video']:
            off_dict = full_off_dict['video'][chosen_prompt]
        else:
            off_dict = {'off_by_zero': [], 'off_by_one': [], 'off_by_five': [], 'total': 0}
        for category in tqdm(categories, total=len(categories)):
            ground_truth_file = f"{args.ground_truth_path}/office1_{category}.json"
            category_responses = {} if category not in responses[chosen_prompt] else responses[chosen_prompt][category]
            for video in tqdm(os.listdir(f"{args.data_path}/base_version/{category}")):
                # print(video.split('.')[0] in category_responses, video.split('.')[0], category_responses.keys())
                # 1/0
                if video.split('.')[0] in category_responses:
                    continue
                rsps, gt_val = process_video(category, video, ground_truth_file, args.data_path, chosen_prompt=chosen_prompt, chosen_model=args.model, qwen_inference=qwen_inference, responses=category_responses)
                if rsps is not None and gt_val is not None:
                    off_dict = update_off_dict(off_dict, rsps, gt_val, video)
                full_off_dict['video'][chosen_prompt] = off_dict
                num_off_dict = {k: len(v) for k, v in off_dict.items() if type(v)==list}
                full_off_dict['num'][chosen_prompt] = num_off_dict
                with open(output_file, "w") as f:
                    json.dump(full_off_dict, f)
                responses[chosen_prompt][category] = category_responses
                with open(output_file_responses, "w") as f:
                    json.dump(responses, f)
        num_off_dict = {k: len(v) for k, v in off_dict.items() if type(v)==list}
        full_off_dict['num'][chosen_prompt] = num_off_dict
        full_off_dict['video'][chosen_prompt] = off_dict
        if off_dict['total'] > 0:
            off_by_zero = len(off_dict['off_by_zero']) / off_dict['total']
            off_by_one = len(off_dict['off_by_one']) / off_dict['total']
            off_by_five = len(off_dict['off_by_five']) / off_dict['total']
            print(f"Off by zero: {off_by_zero}")
            print(f"Off by one: {off_by_one}")
            print(f"Off by five: {off_by_five}")
            print(f"Total: {off_dict['total']}") #Should be 200
    
    print("Evaluation complete.")
    json.dump(full_off_dict, open(output_file, "w"))
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()