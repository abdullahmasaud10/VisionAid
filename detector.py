"""
detector.py - YOLOv8 Object Detector Module
"""
import numpy as np
import cv2
import logging
from config import CLASS_NAMES

class Detector:
    def __init__(self, model_path, conf_threshold=0.10):
        self.conf_threshold = conf_threshold
        try:
            self.net = cv2.dnn.readNet(model_path)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            logging.info("YOLOv8 Detector Initialized.")
        except Exception as e:
            logging.error(f"Engine Load Error: {e}")

    def detect(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
        self.net.setInput(blob)
        
        outputs = self.net.forward()
        output = outputs[0]
        
        # Ensure correct output shape [8400, 84]
        if output.shape[0] < output.shape[1]:
            output = output.transpose()
            
        results = []
        for row in output:
            scores = row[4:]
            conf = np.max(scores)
            
            if conf > self.conf_threshold:
                class_id = np.argmax(scores)
                xc, yc, rw, rh = row[:4]
                
                if xc < 1.0 and rw < 1.0:
                    x1 = int((xc - rw/2) * w)
                    y1 = int((yc - rh/2) * h)
                    x2 = int((xc + rw/2) * w)
                    y2 = int((yc + rh/2) * h)
                else:
                    x1 = int((xc - rw/2) * w / 640)
                    y1 = int((yc - rh/2) * h / 640)
                    x2 = int((xc + rw/2) * w / 640)
                    y2 = int((yc + rh/2) * h / 640)
                
                if (x2 - x1) > 5 and (y2 - y1) > 5:
                    results.append({
                        "box": [x1, y1, x2, y2],
                        "class_id": int(class_id),
                        "confidence": float(conf)
                    })

        indices = cv2.dnn.NMSBoxes([r['box'] for r in results], [r['confidence'] for r in results], self.conf_threshold, 0.45)
        
        final_results = []
        if len(indices) > 0:
            for i in indices.flatten():
                final_results.append(results[i])
        
        return final_results

