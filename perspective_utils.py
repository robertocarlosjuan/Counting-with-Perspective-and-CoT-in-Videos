import re
import json

def clean_and_parse_camera_json(raw_str):
    # Extract all JSON blocks
    print(raw_str)
    json_blocks = re.findall(r"```json\s*(\{.*?\})\s*```", raw_str, re.DOTALL)
    parsed_outputs = []

    for block in json_blocks:
        # Quick fixes for common issues
        fixed = block
        fixed = fixed.replace('utz_level', 'zoom_level')

        # Ensure commas between blocks
        fixed = re.sub(r'("vertical":\s*".*?")\s*("zoom_level")', r'\1,\n"\2', fixed)

        try:
            parsed = json.loads(fixed)
            parsed_outputs.append(parsed)
        except json.JSONDecodeError as e:
            print("Failed to parse one block:", e)
    return parsed_outputs

# structured_perspective_prompt = """
# As a proficient video understanding model, your task is to analyze the camera perspective and provide a structured description of the camera’s motion throughout the video. Please provide your response in JSON format.

# Use this JSON schema:

# CameraMotion = {
#   "translational_movement": {
#     "forward_backward": str,     # "Yes" or "No"
#     "side_to_side": str,         # "Yes" or "No"
#     "vertical": str              # "Yes" or "No"
#   },
#   "rotational_movement": {
#     "pitch": str,                # "Yes" or "No"
#     "yaw": str,                  # "Yes" or "No"
#     "roll": str                  # "Yes" or "No"
#   },
#   "zoom_level": {
#     "zoom": str                  # "Yes" or "No"
#   }
# }

# Return: CameraMotion
# """

# structured_perspective_response_schema = {
#     "type": "object",
#     "properties": {
#         "translational_movement": {
#             "type": "object",
#             "properties": {
#                 "forward_backward": {"type": "string", "description": "Yes or No, with optional brief description"},
#                 "side_to_side": {"type": "string", "description": "Yes or No, with optional brief description"},
#                 "vertical": {"type": "string", "description": "Yes or No, with optional brief description"}
#             },
#             "required": ["forward_backward", "side_to_side", "vertical"]
#         },
#         "rotational_movement": {
#             "type": "object",
#             "properties": {
#                 "pitch": {"type": "string", "description": "Yes or No, with optional brief description"},
#                 "yaw": {"type": "string", "description": "Yes or No, with optional brief description"},
#                 "roll": {"type": "string", "description": "Yes or No, with optional brief description"}
#             },
#             "required": ["pitch", "yaw", "roll"]
#         },
#         "zoom_level": {
#             "type": "object",
#             "properties": {
#                 "zoom": {"type": "string", "description": "Yes or No, with optional brief description"}
#             },
#             "required": ["zoom"]
#         }
#     },
#     "required": ["translational_movement", "rotational_movement", "zoom_level"]
# }

structured_perspective_prompt = """
As a proficient video understanding model, your task is to analyze the camera perspective and provide a structured description of the camera’s motion throughout the video. Please provide your response in JSON format.

Use this JSON schema:

CameraMotion = {
  "translational_movement": {
    "forward_backward": {
      "status": str,     # "Yes" or "No"
      "direction": str   # e.g. "forward" or "backward" or "forward then backward" or "backward then forward" (omit or leave empty if "No")
    },
    "side_to_side": {
      "status": str,     # "Yes" or "No"
      "direction": str   # e.g. "right" or "left" or "right then left" or "left then right" (omit or leave empty if "No")
    },
    "vertical": {
      "status": str,     # "Yes" or "No"
      "direction": str   # e.g. "up" or "down" or "up then down" or "down then up" (omit or leave empty if "No")
    }
  },
  "rotational_movement": {
    "pitch": {
      "status": str,     # "Yes" or "No"
      "direction": str   # e.g. "tilting up" or "tilting down" or "tilting up then down" or "tilting down then up" (omit or leave empty if "No")
    },
    "yaw": {
      "status": str,     # "Yes" or "No"
      "direction": str   # e.g. "panning right" or "panning left" or "panning right then left" or "panning left then right" (omit or leave empty if "No")
    },
    "roll": {
      "status": str,     # "Yes" or "No"
      "direction": str   # e.g. "rolling right" or "rolling left" or "rolling right then left" or "rolling left then right" (omit or leave empty if "No")
    }
  },
  "zoom_level": {
    "zoom": {
      "status": str,     # "Yes" or "No"
      "direction": str   # e.g. "zooming in" or "zooming out" or "zooming in then out" or "zooming out then in" (omit or leave empty if "No")
    }
  }
}

Return: CameraMotion
"""

structured_perspective_generation_config = {
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "object",
        "properties": {
            "translational_movement": {
                "type": "object",
                "properties": {
                    "forward_backward": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "direction": {"type": "string"}
                        },
                        "required": ["status"]
                    },
                    "side_to_side": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "direction": {"type": "string"}
                        },
                        "required": ["status"]
                    },
                    "vertical": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "direction": {"type": "string"}
                        },
                        "required": ["status"]
                    }
                },
                "required": ["forward_backward", "side_to_side", "vertical"]
            },
            "rotational_movement": {
                "type": "object",
                "properties": {
                    "pitch": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "direction": {"type": "string"}
                        },
                        "required": ["status"]
                    },
                    "yaw": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "direction": {"type": "string"}
                        },
                        "required": ["status"]
                    },
                    "roll": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "direction": {"type": "string"}
                        },
                        "required": ["status"]
                    }
                },
                "required": ["pitch", "yaw", "roll"]
            },
            "zoom_level": {
                "type": "object",
                "properties": {
                    "zoom": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "direction": {"type": "string"}
                        },
                        "required": ["status"]
                    }
                },
                "required": ["zoom"]
            }
        },
        "required": ["translational_movement", "rotational_movement", "zoom_level"]
    }
}

