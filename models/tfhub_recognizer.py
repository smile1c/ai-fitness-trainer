import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import cv2

class TFHubExerciseRecognizer:
    def __init__(self):
        """Initialize TensorFlow Hub MoveNet model"""
        print("Loading TensorFlow Hub MoveNet model...")
        
        # Load MoveNet Single Pose Thunder model
        self.model = hub.load('https://tfhub.dev/google/movenet/singlepose/thunder/4')
        self.movenet = self.model.signatures['serving_default']
        
        # Exercise classification based on pose patterns
        self.exercise_history = []
        self.history_size = 30
        
        print("✅ Model loaded successfully!")
    
    def preprocess_image(self, image):
        """Preprocess image for MoveNet"""
        # Resize to 256x256
        img = cv2.resize(image, (256, 256))
        
        # Convert to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        img = tf.cast(img, dtype=tf.int32)
        
        # Add batch dimension
        img = tf.expand_dims(img, axis=0)
        
        return img
    
    def extract_keypoints(self, image):
        """Extract keypoints from image using MoveNet"""
        # Preprocess
        input_image = self.preprocess_image(image)
        
        # Run inference
        outputs = self.movenet(input_image)
        
        # Extract keypoints
        keypoints = outputs['output_0'].numpy()[0, 0, :, :]
        
        return keypoints
    
    def calculate_angles(self, keypoints):
        """Calculate joint angles from keypoints"""
        # MoveNet keypoints indices:
        # 0: nose, 5: left_shoulder, 6: right_shoulder
        # 7: left_elbow, 8: right_elbow, 9: left_wrist, 10: right_wrist
        # 11: left_hip, 12: right_hip, 13: left_knee, 14: right_knee
        # 15: left_ankle, 16: right_ankle
        
        def angle_between_points(p1, p2, p3):
            """Calculate angle at p2"""
            v1 = p1 - p2
            v2 = p3 - p2
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.degrees(np.arccos(cos_angle))
            
            return angle
        
        # Extract coordinates (y, x, confidence)
        coords = keypoints[:, :2]
        
        angles = {}
        
        # Left elbow angle
        angles['left_elbow'] = angle_between_points(
            coords[5], coords[7], coords[9]  # shoulder-elbow-wrist
        )
        
        # Right elbow angle
        angles['right_elbow'] = angle_between_points(
            coords[6], coords[8], coords[10]
        )
        
        # Left knee angle
        angles['left_knee'] = angle_between_points(
            coords[11], coords[13], coords[15]  # hip-knee-ankle
        )
        
        # Right knee angle
        angles['right_knee'] = angle_between_points(
            coords[12], coords[14], coords[16]
        )
        
        # Left hip angle
        angles['left_hip'] = angle_between_points(
            coords[5], coords[11], coords[13]  # shoulder-hip-knee
        )
        
        # Right hip angle
        angles['right_hip'] = angle_between_points(
            coords[6], coords[12], coords[14]
        )
        
        return angles
    
    def classify_exercise(self, keypoints, angles):
        """Classify exercise based on pose and angles"""
        
        # Average angles
        avg_knee = (angles['left_knee'] + angles['right_knee']) / 2
        avg_elbow = (angles['left_elbow'] + angles['right_elbow']) / 2
        avg_hip = (angles['left_hip'] + angles['right_hip']) / 2
        
        # Check body position (standing vs ground)
        hip_y = (keypoints[11][0] + keypoints[12][0]) / 2
        ankle_y = (keypoints[15][0] + keypoints[16][0]) / 2
        body_height = abs(hip_y - ankle_y)
        
        # Store in history
        self.exercise_history.append({
            'knee': avg_knee,
            'elbow': avg_elbow,
            'hip': avg_hip,
            'height': body_height
        })
        
        if len(self.exercise_history) > self.history_size:
            self.exercise_history.pop(0)
        
        if len(self.exercise_history) < 10:
            return 'detecting', 0.0
        
        # Calculate variance
        knee_var = np.var([h['knee'] for h in self.exercise_history])
        elbow_var = np.var([h['elbow'] for h in self.exercise_history])
        hip_var = np.var([h['hip'] for h in self.exercise_history])
        height_var = np.var([h['height'] for h in self.exercise_history])
        
        # Calculate ranges
        knee_range = max([h['knee'] for h in self.exercise_history]) - min([h['knee'] for h in self.exercise_history])
        elbow_range = max([h['elbow'] for h in self.exercise_history]) - min([h['elbow'] for h in self.exercise_history])
        
        # Classification logic
        scores = {}
        
        # 1. SQUAT
        if body_height > 0.3:
            scores['squat'] = 0.0
            if knee_var > 200:
                scores['squat'] += 0.4
            if 100 < avg_knee < 160:
                scores['squat'] += 0.3
            if avg_elbow > 150:
                scores['squat'] += 0.2
            if 120 < avg_hip < 170:
                scores['squat'] += 0.1
        else:
            scores['squat'] = 0.0
        
        # 2. PUSH-UP
        if body_height < 0.3:
            scores['pushup'] = 0.0
            if elbow_var > 200:
                scores['pushup'] += 0.4
            if 90 < avg_elbow < 150:
                scores['pushup'] += 0.3
            if 150 < avg_hip < 190:
                scores['pushup'] += 0.2
        else:
            scores['pushup'] = 0.0
        
        # 3. PLANK
        if body_height < 0.3:
            scores['plank'] = 0.0
            if elbow_var < 100 and knee_var < 100:
                scores['plank'] += 0.5
            if 160 < avg_hip < 190:
                scores['plank'] += 0.3
            if 70 < avg_elbow < 110:
                scores['plank'] += 0.2
        else:
            scores['plank'] = 0.0
        
        # 4. LUNGES
        if body_height > 0.25:
            knee_diff = abs(angles['left_knee'] - angles['right_knee'])
            scores['lunges'] = 0.0
            if knee_diff > 30:
                scores['lunges'] += 0.4
            if min(angles['left_knee'], angles['right_knee']) < 120:
                scores['lunges'] += 0.3
            if avg_elbow > 150:
                scores['lunges'] += 0.2
        else:
            scores['lunges'] = 0.0
        
        # 5. JUMPING JACKS
        if body_height > 0.3:
            scores['jumping_jacks'] = 0.0
            if elbow_var > 300 and knee_var > 200:
                scores['jumping_jacks'] += 0.5
            if hip_var > 200:
                scores['jumping_jacks'] += 0.3
        else:
            scores['jumping_jacks'] = 0.0
        
        # 6. SIT-UPS
        if body_height < 0.2:
            scores['situp'] = 0.0
            if hip_var > 300:
                scores['situp'] += 0.5
            if avg_knee < 120:
                scores['situp'] += 0.3
        else:
            scores['situp'] = 0.0
        
        # 7. HIGH KNEES
        if body_height > 0.25:
            scores['high_knees'] = 0.0
            if knee_var > 400:
                scores['high_knees'] += 0.5
            if hip_var > 300:
                scores['high_knees'] += 0.3
        else:
            scores['high_knees'] = 0.0
        
        # 8. BURPEES
        scores['burpees'] = 0.0
        if height_var > 0.05:
            scores['burpees'] += 0.6
            if elbow_var > 200:
                scores['burpees'] += 0.2
            if knee_var > 200:
                scores['burpees'] += 0.2
        
        # 9. MOUNTAIN CLIMBERS
        if body_height < 0.3:
            scores['mountain_climbers'] = 0.0
            if knee_var > 300:
                scores['mountain_climbers'] += 0.5
            if 150 < avg_hip < 190:
                scores['mountain_climbers'] += 0.3
            if avg_elbow > 150:
                scores['mountain_climbers'] += 0.2
        else:
            scores['mountain_climbers'] = 0.0
        
        # 10. SIDE PLANK
        if body_height < 0.3:
            shoulder_diff_x = abs(keypoints[5][1] - keypoints[6][1])
            scores['side_plank'] = 0.0
            if shoulder_diff_x > 0.2:
                scores['side_plank'] += 0.5
            if elbow_var < 100:
                scores['side_plank'] += 0.3
        else:
            scores['side_plank'] = 0.0
        
        # 11. RUNNING IN PLACE
        if body_height > 0.3:
            scores['running'] = 0.0
            if knee_var > 400:
                scores['running'] += 0.5
            if knee_range > 80:
                scores['running'] += 0.3
            if elbow_var > 200:
                scores['running'] += 0.2
        else:
            scores['running'] = 0.0
        
        # 12. CRUNCHES
        if body_height < 0.2:
            scores['crunches'] = 0.0
            if 150 < hip_var < 400:
                scores['crunches'] += 0.5
            if avg_knee < 110:
                scores['crunches'] += 0.3
        else:
            scores['crunches'] = 0.0
        
        # 13. LEG RAISES
        if body_height < 0.15:
            scores['leg_raises'] = 0.0
            if knee_var > 300:
                scores['leg_raises'] += 0.5
            if avg_hip > 160:
                scores['leg_raises'] += 0.3
        else:
            scores['leg_raises'] = 0.0
        
        # 14. BICYCLE CRUNCHES
        if body_height < 0.2:
            knee_diff = abs(angles['left_knee'] - angles['right_knee'])
            scores['bicycle_crunches'] = 0.0
            if knee_diff > 40 and knee_var > 300:
                scores['bicycle_crunches'] += 0.5
            if elbow_var > 200:
                scores['bicycle_crunches'] += 0.3
        else:
            scores['bicycle_crunches'] = 0.0
        
        # 15. STANDING KNEE RAISES
        if body_height > 0.3:
            knee_diff = abs(angles['left_knee'] - angles['right_knee'])
            scores['standing_knee_raises'] = 0.0
            if knee_diff > 50 and knee_var > 200:
                scores['standing_knee_raises'] += 0.5
            if elbow_var < 100:
                scores['standing_knee_raises'] += 0.3
        else:
            scores['standing_knee_raises'] = 0.0
        
        # 16. WALL SIT
        if body_height > 0.2:
            scores['wall_sit'] = 0.0
            if knee_var < 50:
                scores['wall_sit'] += 0.5
            if 80 < avg_knee < 110:
                scores['wall_sit'] += 0.4
        else:
            scores['wall_sit'] = 0.0
        
        # 17. GLUTE BRIDGE
        if body_height < 0.25:
            scores['glute_bridge'] = 0.0
            if hip_var > 200:
                scores['glute_bridge'] += 0.5
            if avg_knee < 120:
                scores['glute_bridge'] += 0.3
        else:
            scores['glute_bridge'] = 0.0
        
        # 18. JUMPING
        if body_height > 0.3:
            scores['jumping'] = 0.0
            if height_var > 0.03:
                scores['jumping'] += 0.6
            if knee_var > 200:
                scores['jumping'] += 0.3
        else:
            scores['jumping'] = 0.0
        
        # 19. STAR JUMPS
        if body_height > 0.3:
            scores['star_jumps'] = 0.0
            if elbow_var > 400 and knee_var > 300:
                scores['star_jumps'] += 0.5
            if elbow_range > 100:
                scores['star_jumps'] += 0.3
        else:
            scores['star_jumps'] = 0.0
        
        # 20. SQUAT JUMPS
        if body_height > 0.25:
            scores['squat_jumps'] = 0.0
            if knee_var > 400 and height_var > 0.03:
                scores['squat_jumps'] += 0.6
            if knee_range > 100:
                scores['squat_jumps'] += 0.3
        else:
            scores['squat_jumps'] = 0.0
        
        # Get best match
        if not scores or max(scores.values()) < 0.3:
            return 'unknown', 0.0
        
        exercise = max(scores, key=scores.get)
        confidence = scores[exercise]
        
        return exercise, confidence
    
    def detect_exercise(self, image):
        """Main detection function"""
        try:
            # Extract keypoints
            keypoints = self.extract_keypoints(image)
            
            # Calculate angles
            angles = self.calculate_angles(keypoints)
            
            # Classify exercise
            exercise, confidence = self.classify_exercise(keypoints, angles)
            
            return exercise, confidence, keypoints, angles
            
        except Exception as e:
            print(f"Error in detection: {e}")
            return 'error', 0.0, None, {}
    
    def reset(self):
        """Reset history"""
        self.exercise_history = []
    
    def draw_keypoints(self, image, keypoints):
        """Draw keypoints on image"""
        h, w = image.shape[:2]
        
        # Draw connections
        connections = [
            (5, 7), (7, 9),    # Left arm
            (6, 8), (8, 10),   # Right arm
            (11, 13), (13, 15),  # Left leg
            (12, 14), (14, 16),  # Right leg
            (5, 6),             # Shoulders
            (11, 12),           # Hips
            (5, 11), (6, 12)    # Torso
        ]
        
        for connection in connections:
            y1, x1, conf1 = keypoints[connection[0]]
            y2, x2, conf2 = keypoints[connection[1]]
            
            if conf1 > 0.3 and conf2 > 0.3:
                pt1 = (int(x1 * w), int(y1 * h))
                pt2 = (int(x2 * w), int(y2 * h))
                cv2.line(image, pt1, pt2, (0, 255, 0), 2)
        
        # Draw keypoints
        for i, (y, x, conf) in enumerate(keypoints):
            if conf > 0.3:
                pt = (int(x * w), int(y * h))
                cv2.circle(image, pt, 5, (0, 255, 255), -1)
        
        return image