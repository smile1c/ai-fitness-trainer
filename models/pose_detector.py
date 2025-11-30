import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    def __init__(self, 
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
    def detect_pose(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        return results, image_rgb
    
    def draw_landmarks(self, image, results):
        annotated_image = image.copy()
        
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        
        return annotated_image
    
    def draw_angles(self, image, landmarks, angles, feedback):
        h, w, _ = image.shape
        
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (w, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)
        
        y_offset = 40
        
        if 'detected' in feedback:
            cv2.putText(image, feedback['detected'], (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 3, cv2.LINE_AA)
            y_offset += 50
        
        if landmarks:
            left_knee_pos = (int(landmarks[25].x * w), int(landmarks[25].y * h))
            cv2.circle(image, left_knee_pos, 8, (0, 255, 255), -1)
            cv2.putText(image, f"{int(angles.get('left_knee', 0))} deg", 
                       (left_knee_pos[0] + 15, left_knee_pos[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            right_knee_pos = (int(landmarks[26].x * w), int(landmarks[26].y * h))
            cv2.circle(image, right_knee_pos, 8, (0, 255, 255), -1)
            cv2.putText(image, f"{int(angles.get('right_knee', 0))} deg", 
                       (right_knee_pos[0] + 15, right_knee_pos[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        for key, message in feedback.items():
            if key in ['detected', 'reps']:
                continue
                
            if "Perfect" in message or "Good" in message:
                color = (0, 255, 0)
            elif "Watch" in message or "Adjust" in message or "Detecting" in message:
                color = (0, 165, 255)
            else:
                color = (0, 0, 255)
            
            cv2.putText(image, message, (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
            y_offset += 35
        
        return image
    
    def close(self):
        self.pose.close()