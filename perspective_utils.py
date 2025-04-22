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

structured_perspective_prompt = """
As a proficient video understanding model, your task is to analyze the camera perspective and provide a structured description of how the camera moves throughout the video.

Each time the **camera's motion pattern changes** — such as starting or stopping a movement, or switching direction (e.g. from moving forward to moving left, or from yawing right to becoming static) — create a **new entry** in the list.

For each entry:
- Provide the **start and end time** in seconds
- Report whether the camera was moving in each of the 14 directions using **"Yes"** or **"No"**
- Do **not omit** any motion direction; include all 14 fields, even if set to "No"
- Return your output as a JSON list of these motion segments

Use only the following 14 motion directions:
- Translational: `"forward"`, `"backward"`, `"left"`, `"right"`, `"up"`, `"down"`
- Rotational: `"pitch_up"`, `"pitch_down"`, `"yaw_left"`, `"yaw_right"`, `"roll_left"`, `"roll_right"`
- Zoom: `"zoom_in"`, `"zoom_out"`

Example format:
[
  {
    "start_time": 0.0,
    "end_time": 2.5,
    "camera_motion": {
      "translational_movement": {
        "forward": "Yes", "backward": "No", "left": "No", "right": "No", "up": "No", "down": "No"
      },
      "rotational_movement": {
        "pitch_up": "No", "pitch_down": "No", "yaw_left": "No", "yaw_right": "Yes", "roll_left": "No", "roll_right": "No"
      },
      "zoom_level": {
        "zoom_in": "No", "zoom_out": "No"
      }
    }
  },
  ...
]
"""

structured_perspective_generation_config = {
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "start_time": {"type": "number"},
                "end_time": {"type": "number"},
                "camera_motion": {
                    "type": "object",
                    "properties": {
                        "translational_movement": {
                            "type": "object",
                            "properties": {
                                "forward": {"type": "string", "enum": ["Yes", "No"]},
                                "backward": {"type": "string", "enum": ["Yes", "No"]},
                                "left": {"type": "string", "enum": ["Yes", "No"]},
                                "right": {"type": "string", "enum": ["Yes", "No"]},
                                "up": {"type": "string", "enum": ["Yes", "No"]},
                                "down": {"type": "string", "enum": ["Yes", "No"]}
                            },
                            "required": ["forward", "backward", "left", "right", "up", "down"]
                        },
                        "rotational_movement": {
                            "type": "object",
                            "properties": {
                                "pitch_up": {"type": "string", "enum": ["Yes", "No"]},
                                "pitch_down": {"type": "string", "enum": ["Yes", "No"]},
                                "yaw_left": {"type": "string", "enum": ["Yes", "No"]},
                                "yaw_right": {"type": "string", "enum": ["Yes", "No"]},
                                "roll_left": {"type": "string", "enum": ["Yes", "No"]},
                                "roll_right": {"type": "string", "enum": ["Yes", "No"]}
                            },
                            "required": ["pitch_up", "pitch_down", "yaw_left", "yaw_right", "roll_left", "roll_right"]
                        },
                        "zoom_level": {
                            "type": "object",
                            "properties": {
                                "zoom_in": {"type": "string", "enum": ["Yes", "No"]},
                                "zoom_out": {"type": "string", "enum": ["Yes", "No"]}
                            },
                            "required": ["zoom_in", "zoom_out"]
                        }
                    },
                    "required": ["translational_movement", "rotational_movement", "zoom_level"]
                }
            },
            "required": ["start_time", "end_time", "camera_motion"]
        }
    }
}






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

# structured_perspective_prompt = """
# As a proficient video understanding model, your task is to analyze the camera perspective and provide a structured description of the camera’s motion throughout the video. Please provide your response in JSON format.

# Use this JSON schema:

# CameraMotion = {
#   "translational_movement": {
#     "forward_backward": {
#       "status": str,     # "Yes" or "No"
#       "direction": str   # e.g. "forward" or "backward" or "forward then backward" or "backward then forward" (omit or leave empty if "No")
#     },
#     "side_to_side": {
#       "status": str,     # "Yes" or "No"
#       "direction": str   # e.g. "right" or "left" or "right then left" or "left then right" (omit or leave empty if "No")
#     },
#     "vertical": {
#       "status": str,     # "Yes" or "No"
#       "direction": str   # e.g. "up" or "down" or "up then down" or "down then up" (omit or leave empty if "No")
#     }
#   },
#   "rotational_movement": {
#     "pitch": {
#       "status": str,     # "Yes" or "No"
#       "direction": str   # e.g. "tilting up" or "tilting down" or "tilting up then down" or "tilting down then up" (omit or leave empty if "No")
#     },
#     "yaw": {
#       "status": str,     # "Yes" or "No"
#       "direction": str   # e.g. "panning right" or "panning left" or "panning right then left" or "panning left then right" (omit or leave empty if "No")
#     },
#     "roll": {
#       "status": str,     # "Yes" or "No"
#       "direction": str   # e.g. "rolling right" or "rolling left" or "rolling right then left" or "rolling left then right" (omit or leave empty if "No")
#     }
#   },
#   "zoom_level": {
#     "zoom": {
#       "status": str,     # "Yes" or "No"
#       "direction": str   # e.g. "zooming in" or "zooming out" or "zooming in then out" or "zooming out then in" (omit or leave empty if "No")
#     }
#   }
# }

# Return: CameraMotion
# """

# structured_perspective_generation_config = {
#     "response_mime_type": "application/json",
#     "response_schema": {
#         "type": "object",
#         "properties": {
#             "translational_movement": {
#                 "type": "object",
#                 "properties": {
#                     "forward_backward": {
#                         "type": "object",
#                         "properties": {
#                             "status": {"type": "string"},
#                             "direction": {"type": "string"}
#                         },
#                         "required": ["status"]
#                     },
#                     "side_to_side": {
#                         "type": "object",
#                         "properties": {
#                             "status": {"type": "string"},
#                             "direction": {"type": "string"}
#                         },
#                         "required": ["status"]
#                     },
#                     "vertical": {
#                         "type": "object",
#                         "properties": {
#                             "status": {"type": "string"},
#                             "direction": {"type": "string"}
#                         },
#                         "required": ["status"]
#                     }
#                 },
#                 "required": ["forward_backward", "side_to_side", "vertical"]
#             },
#             "rotational_movement": {
#                 "type": "object",
#                 "properties": {
#                     "pitch": {
#                         "type": "object",
#                         "properties": {
#                             "status": {"type": "string"},
#                             "direction": {"type": "string"}
#                         },
#                         "required": ["status"]
#                     },
#                     "yaw": {
#                         "type": "object",
#                         "properties": {
#                             "status": {"type": "string"},
#                             "direction": {"type": "string"}
#                         },
#                         "required": ["status"]
#                     },
#                     "roll": {
#                         "type": "object",
#                         "properties": {
#                             "status": {"type": "string"},
#                             "direction": {"type": "string"}
#                         },
#                         "required": ["status"]
#                     }
#                 },
#                 "required": ["pitch", "yaw", "roll"]
#             },
#             "zoom_level": {
#                 "type": "object",
#                 "properties": {
#                     "zoom": {
#                         "type": "object",
#                         "properties": {
#                             "status": {"type": "string"},
#                             "direction": {"type": "string"}
#                         },
#                         "required": ["status"]
#                     }
#                 },
#                 "required": ["zoom"]
#             }
#         },
#         "required": ["translational_movement", "rotational_movement", "zoom_level"]
#     }
# }

