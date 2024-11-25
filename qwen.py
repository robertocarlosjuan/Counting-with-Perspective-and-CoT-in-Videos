import os
os.environ["HF_HOME"] = "/home/hice1/che321/scratch/.cache"
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info

class QwenInference():

    def __init__(self, model_path="Qwen/Qwen2-VL-7B-Instruct"):

        quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_path, torch_dtype="auto", device_map=0, 
        attn_implementation="flash_attention_2", quantization_config=quantization_config)
        self.processor = AutoProcessor.from_pretrained(model_path)

    def run(self, inputs):

        content = []
        for inp in inputs:
            inp_type = "text"
            if inp.endswith('.jpg'):
                inp_type = "image"
            elif inp.endswith('.mp4'):
                inp_type = "video"
            content.append({"type": inp_type, inp_type: inp})
        
        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]

        # Preparation for inference
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text[0]