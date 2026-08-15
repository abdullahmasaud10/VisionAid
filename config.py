"""
config.py - VisionAid System Configuration
"""
GPIO_TRIG = 23
GPIO_ECHO = 24

DISTANCE_CRITICAL = 0.5
DISTANCE_WARNING  = 1.5

CAMERA_INDEX     = 0
CAMERA_WIDTH     = 640
CAMERA_HEIGHT    = 480
CAMERA_FPS       = 30

# AI Settings
INPUT_SIZE           = (640, 640) 
CONFIDENCE_THRESHOLD  = 0.35 
MODEL_PATH           = "model/yolov8n.onnx"

LANGUAGE = "ENGLISH"
SPEECH_COOLDOWN = 3.0
FLASK_PORT = 5001

# --- STANDARD COCO MAPPING ---
CLASS_NAMES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
    "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]

URDU_DICT = {
    # Objects
    "person": "insan", 
    "chair": "kursi", 
    "table": "meiz", 
    "car": "gaari", 
    "bus": "bus", 
    "stop sign": "Ruk jao",
    "backpack": "basta", 
    "bottle": "botal", 
    "cup": "pyala", 
    "bench": "bench", 
    "potted plant": "gamla",
    
    # Directions
    "ahead": "theek agay", 
    "left": "baayein", 
    "right": "daayein",
    
    # Navigation Phrases
    "Warning!": "Khabardar!",
    "Stop!": "Ruk jayen!",
    "Turn right": "Daayein murein",
    "Turn left": "Baayein murein",
    "on your": "aap ke",
    "metres away": "meter door hai",
    "metres": "meter",
    "detected": "dekha gaya hai"
}
