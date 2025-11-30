import numpy as np
from exercise_standards import EXERCISE_STANDARDS, get_rep_thresholds, get_feedback_criteria

class ExerciseAnalyzer:
    def __init__(self, exercise_type='squat'):
        self.exercise_type = exercise_type
        self.rep_count = 0
        self.rep_stage = None
        self.feedback = {}
        self.frame_buffer = []
        
        # Load research-backed thresholds for this exercise
        thresholds = get_rep_thresholds(exercise_type)
        if thresholds:
            self.buffer_size = thresholds.get('buffer_size', 12)
            self.cooldown_threshold = thresholds.get('cooldown_frames', 20)
        else:
            self.buffer_size = 12
            self.cooldown_threshold = 20
            
        self.cooldown_frames = 0
        
    def analyze_squat(self, landmarks, angles):
        feedback = {}
        avg_knee = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
        
        self.frame_buffer.append(avg_knee)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        # Detailed feedback
        if avg_knee < 90:
            feedback['depth'] = "Excellent depth!"
        elif avg_knee < 100:
            feedback['depth'] = "Perfect depth!"
        elif avg_knee < 120:
            feedback['depth'] = "Good - go lower"
        else:
            feedback['depth'] = "Lower more"
        
        if 80 < angles.get('back', 90) < 100:
            feedback['back'] = "Perfect posture"
        elif angles.get('back', 90) < 80:
            feedback['back'] = "Stand more upright"
        else:
            feedback['back'] = "Lean forward slightly"
        
        # Cooldown
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        # High accuracy rep counting
        if len(self.frame_buffer) >= self.buffer_size:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            min_buffer = min(self.frame_buffer)
            max_buffer = max(self.frame_buffer)
            range_buffer = max_buffer - min_buffer
            
            # Standing (UP) - must be truly straight
            if avg_buffer > 168 and max_buffer > 172 and self.rep_stage != "up":
                self.rep_stage = "up"
            
            # Squatting (DOWN) - must go deep + not in cooldown
            if avg_buffer < 92 and min_buffer < 85 and self.rep_stage == "up" and self.cooldown_frames == 0 and range_buffer > 50:
                self.rep_stage = "down"
                self.rep_count += 1
                self.cooldown_frames = self.cooldown_threshold
        
        return feedback
    
    def analyze_pushup(self, landmarks, angles):
        feedback = {}
        avg_elbow = (angles.get('left_elbow', 180) + angles.get('right_elbow', 180)) / 2
        
        self.frame_buffer.append(avg_elbow)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        if avg_elbow < 80:
            feedback['depth'] = "Excellent depth!"
        elif avg_elbow < 100:
            feedback['depth'] = "Perfect depth!"
        elif avg_elbow < 120:
            feedback['depth'] = "Good - go lower"
        else:
            feedback['depth'] = "Lower chest more"
        
        avg_hip = (angles.get('left_hip', 180) + angles.get('right_hip', 180)) / 2
        if 160 < avg_hip < 190:
            feedback['body'] = "Perfect form"
        elif avg_hip < 160:
            feedback['body'] = "Hips too high"
        else:
            feedback['body'] = "Don't sag hips"
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= self.buffer_size:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            min_buffer = min(self.frame_buffer)
            max_buffer = max(self.frame_buffer)
            range_buffer = max_buffer - min_buffer
            
            # Arms extended (UP)
            if avg_buffer > 168 and max_buffer > 172 and self.rep_stage != "up":
                self.rep_stage = "up"
            
            # Arms bent (DOWN)
            if avg_buffer < 92 and min_buffer < 85 and self.rep_stage == "up" and self.cooldown_frames == 0 and range_buffer > 50:
                self.rep_stage = "down"
                self.rep_count += 1
                self.cooldown_frames = self.cooldown_threshold
        
        return feedback
    
    def analyze_plank(self, landmarks, angles):
        feedback = {}
        avg_hip = (angles.get('left_hip', 180) + angles.get('right_hip', 180)) / 2
        
        if 165 < avg_hip < 185:
            feedback['alignment'] = "Excellent plank!"
        elif 160 < avg_hip < 190:
            feedback['alignment'] = "Good alignment"
        elif avg_hip < 160:
            feedback['alignment'] = "Hips too high"
        else:
            feedback['alignment'] = "Don't sag hips"
        
        avg_elbow = (angles.get('left_elbow', 180) + angles.get('right_elbow', 180)) / 2
        if 80 < avg_elbow < 100:
            feedback['elbows'] = "Perfect position"
        else:
            feedback['elbows'] = "Adjust elbows"
        
        return feedback
    
    def analyze_lunges(self, landmarks, angles):
        feedback = {}
        
        knee_diff = abs(angles.get('left_knee', 180) - angles.get('right_knee', 180))
        min_knee = min(angles.get('left_knee', 180), angles.get('right_knee', 180))
        
        self.frame_buffer.append(min_knee)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        if knee_diff > 40:
            feedback['position'] = "Excellent depth"
        elif knee_diff > 30:
            feedback['position'] = "Good lunge"
        else:
            feedback['position'] = "Lower front knee"
        
        if min_knee < 80:
            feedback['depth'] = "Perfect!"
        elif min_knee < 90:
            feedback['depth'] = "Excellent"
        elif min_knee < 110:
            feedback['depth'] = "Good"
        else:
            feedback['depth'] = "Go lower"
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= self.buffer_size:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            
            if avg_buffer > 155 and self.rep_stage != "up":
                self.rep_stage = "up"
            
            if avg_buffer < 85 and knee_diff > 35 and self.rep_stage == "up" and self.cooldown_frames == 0:
                self.rep_stage = "down"
                self.rep_count += 1
                self.cooldown_frames = self.cooldown_threshold
        
        return feedback
    
    def analyze_jumping_jacks(self, landmarks, angles):
        feedback = {}
        
        avg_elbow = (angles.get('left_elbow', 180) + angles.get('right_elbow', 180)) / 2
        
        self.frame_buffer.append(avg_elbow)
        if len(self.frame_buffer) > 5:
            self.frame_buffer.pop(0)
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= 5:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            
            if avg_buffer > 172 and self.rep_stage != "up" and self.cooldown_frames == 0:
                feedback['arms'] = "Arms up!"
                self.rep_stage = "up"
                self.rep_count += 1
                self.cooldown_frames = 8
            elif avg_buffer < 145:
                feedback['arms'] = "Raise arms"
                self.rep_stage = "down"
        
        return feedback
    
    def analyze_situp(self, landmarks, angles):
        feedback = {}
        
        avg_hip = (angles.get('left_hip', 180) + angles.get('right_hip', 180)) / 2
        
        self.frame_buffer.append(avg_hip)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= self.buffer_size:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            
            if avg_buffer < 85 and self.rep_stage != "up" and self.cooldown_frames == 0:
                feedback['position'] = "Excellent sit-up!"
                self.rep_stage = "up"
                self.rep_count += 1
                self.cooldown_frames = self.cooldown_threshold
            elif avg_buffer > 125:
                feedback['position'] = "Curl up more"
                self.rep_stage = "down"
        
        return feedback
    
    def analyze_high_knees(self, landmarks, angles):
        feedback = {}
        
        min_knee = min(angles.get('left_knee', 180), angles.get('right_knee', 180))
        if min_knee < 80:
            feedback['height'] = "Excellent height!"
        elif min_knee < 90:
            feedback['height'] = "Good height"
        else:
            feedback['height'] = "Lift higher"
        
        return feedback
    
    def analyze_burpees(self, landmarks, angles):
        feedback = {}
        feedback['status'] = "Keep going!"
        return feedback
    
    def analyze_mountain_climbers(self, landmarks, angles):
        feedback = {}
        
        knee_diff = abs(angles.get('left_knee', 180) - angles.get('right_knee', 180))
        if knee_diff > 50:
            feedback['movement'] = "Excellent pace!"
        elif knee_diff > 40:
            feedback['movement'] = "Good pace"
        else:
            feedback['movement'] = "Move faster"
        
        return feedback
    
    def analyze_side_plank(self, landmarks, angles):
        feedback = {}
        
        avg_hip = (angles.get('left_hip', 180) + angles.get('right_hip', 180)) / 2
        if 165 < avg_hip < 185:
            feedback['alignment'] = "Perfect!"
        elif 160 < avg_hip < 190:
            feedback['alignment'] = "Good"
        else:
            feedback['alignment'] = "Keep straight"
        
        return feedback
    
    def analyze_running(self, landmarks, angles):
        feedback = {}
        
        knee_diff = abs(angles.get('left_knee', 180) - angles.get('right_knee', 180))
        if knee_diff > 60:
            feedback['pace'] = "Excellent pace!"
        elif knee_diff > 50:
            feedback['pace'] = "Good pace"
        else:
            feedback['pace'] = "Run faster"
        
        min_knee = min(angles.get('left_knee', 180), angles.get('right_knee', 180))
        if min_knee < 95:
            feedback['form'] = "Good knee lift!"
        
        return feedback
    
    def analyze_walking(self, landmarks, angles):
        feedback = {}
        
        knee_diff = abs(angles.get('left_knee', 180) - angles.get('right_knee', 180))
        if knee_diff > 25:
            feedback['pace'] = "Good walking!"
        elif knee_diff > 20:
            feedback['pace'] = "Natural pace"
        else:
            feedback['pace'] = "Keep moving"
        
        avg_knee = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
        if 145 < avg_knee < 175:
            feedback['form'] = "Good posture!"
        
        return feedback
    
    def analyze_crunches(self, landmarks, angles):
        feedback = {}
        
        avg_hip = (angles.get('left_hip', 180) + angles.get('right_hip', 180)) / 2
        
        self.frame_buffer.append(avg_hip)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= self.buffer_size:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            
            if avg_buffer < 95 and self.rep_stage != "up" and self.cooldown_frames == 0:
                feedback['position'] = "Great crunch!"
                self.rep_stage = "up"
                self.rep_count += 1
                self.cooldown_frames = self.cooldown_threshold
            else:
                feedback['position'] = "Lift shoulders"
                self.rep_stage = "down"
        
        return feedback
    
    def analyze_leg_raises(self, landmarks, angles):
        feedback = {}
        
        avg_knee = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
        
        self.frame_buffer.append(avg_knee)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        if avg_knee > 165:
            feedback['form'] = "Legs straight!"
        else:
            feedback['form'] = "Straighten legs"
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= self.buffer_size:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            
            if avg_buffer > 155 and self.rep_stage != "up" and self.cooldown_frames == 0:
                self.rep_stage = "up"
                self.rep_count += 1
                self.cooldown_frames = self.cooldown_threshold
            elif avg_buffer < 115:
                self.rep_stage = "down"
        
        return feedback
    
    def analyze_bicycle_crunches(self, landmarks, angles):
        feedback = {}
        
        knee_diff = abs(angles.get('left_knee', 180) - angles.get('right_knee', 180))
        if knee_diff > 50:
            feedback['movement'] = "Excellent rotation!"
        elif knee_diff > 40:
            feedback['movement'] = "Good rotation"
        else:
            feedback['movement'] = "Rotate more"
        
        return feedback
    
    def analyze_standing_knee_raises(self, landmarks, angles):
        feedback = {}
        
        min_knee = min(angles.get('left_knee', 180), angles.get('right_knee', 180))
        
        self.frame_buffer.append(min_knee)
        if len(self.frame_buffer) > 5:
            self.frame_buffer.pop(0)
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= 5:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            
            if avg_buffer < 65 and self.rep_stage != "up" and self.cooldown_frames == 0:
                feedback['height'] = "Perfect height!"
                self.rep_stage = "up"
                self.rep_count += 1
                self.cooldown_frames = 10
            elif avg_buffer > 155:
                feedback['height'] = "Lift higher"
                self.rep_stage = "down"
        
        return feedback
    
    def analyze_wall_sit(self, landmarks, angles):
        feedback = {}
        
        avg_knee = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
        if 85 < avg_knee < 95:
            feedback['position'] = "Perfect 90°!"
        elif 80 < avg_knee < 105:
            feedback['position'] = "Good angle"
        else:
            feedback['position'] = "Adjust position"
        
        feedback['hold'] = "Hold steady"
        
        return feedback
    
    def analyze_glute_bridge(self, landmarks, angles):
        feedback = {}
        
        avg_hip = (angles.get('left_hip', 180) + angles.get('right_hip', 180)) / 2
        
        self.frame_buffer.append(avg_hip)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if len(self.frame_buffer) >= self.buffer_size:
            avg_buffer = sum(self.frame_buffer) / len(self.frame_buffer)
            
            if avg_buffer > 172 and self.rep_stage != "up" and self.cooldown_frames == 0:
                feedback['position'] = "Excellent lift!"
                self.rep_stage = "up"
                self.rep_count += 1
                self.cooldown_frames = self.cooldown_threshold
            else:
                feedback['position'] = "Lift hips"
                self.rep_stage = "down"
        
        return feedback
    
    def analyze_jumping(self, landmarks, angles):
        feedback = {}
        feedback['status'] = "Keep jumping!"
        return feedback
    
    def analyze_star_jumps(self, landmarks, angles):
        feedback = {}
        
        avg_elbow = (angles.get('left_elbow', 180) + angles.get('right_elbow', 180)) / 2
        if avg_elbow > 175:
            feedback['form'] = "Full extension!"
        elif avg_elbow > 170:
            feedback['form'] = "Great form"
        else:
            feedback['form'] = "Extend fully"
        
        return feedback
    
    def analyze_squat_jumps(self, landmarks, angles):
        feedback = {}
        
        avg_knee = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
        if avg_knee < 100:
            feedback['depth'] = "Perfect squat!"
        elif avg_knee < 110:
            feedback['depth'] = "Good squat"
        else:
            feedback['depth'] = "Squat deeper"
        
        feedback['power'] = "Explode up!"
        
        return feedback
    
    def analyze_frame(self, landmarks):
        if not landmarks:
            return {"error": "No pose detected"}, {}
        
        if isinstance(landmarks, dict):
            angles = landmarks
        else:
            from utils.angle_calculator import get_joint_angles
            angles = get_joint_angles(landmarks)
        
        exercise_map = {
            'squat': self.analyze_squat,
            'pushup': self.analyze_pushup,
            'plank': self.analyze_plank,
            'lunges': self.analyze_lunges,
            'jumping_jacks': self.analyze_jumping_jacks,
            'situp': self.analyze_situp,
            'high_knees': self.analyze_high_knees,
            'burpees': self.analyze_burpees,
            'mountain_climbers': self.analyze_mountain_climbers,
            'side_plank': self.analyze_side_plank,
            'running': self.analyze_running,
            'walking': self.analyze_walking,
            'crunches': self.analyze_crunches,
            'leg_raises': self.analyze_leg_raises,
            'bicycle_crunches': self.analyze_bicycle_crunches,
            'standing_knee_raises': self.analyze_standing_knee_raises,
            'wall_sit': self.analyze_wall_sit,
            'glute_bridge': self.analyze_glute_bridge,
            'jumping': self.analyze_jumping,
            'star_jumps': self.analyze_star_jumps,
            'squat_jumps': self.analyze_squat_jumps
        }
        
        if self.exercise_type in exercise_map:
            feedback = exercise_map[self.exercise_type](landmarks, angles)
        else:
            feedback = {"error": "Unknown exercise"}
        
        feedback['reps'] = f"Reps: {self.rep_count}"
        
        return feedback, angles
    
    def reset_counter(self):
        self.rep_count = 0
        self.rep_stage = None
        self.frame_buffer = []
        self.cooldown_frames = 0
    
    def get_summary(self):
        return {
            'exercise': self.exercise_type,
            'total_reps': self.rep_count
        }