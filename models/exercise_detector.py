import numpy as np

class ExerciseDetector:
    def __init__(self):
        self.history = []
        self.window_size = 30
    
    def detect_exercise(self, angles):
        """ตรวจจับว่าท่าไหนจากมุมข้อต่อ"""
        
        avg_knee = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
        avg_elbow = (angles.get('left_elbow', 180) + angles.get('right_elbow', 180)) / 2
        avg_hip = (angles.get('left_hip', 180) + angles.get('right_hip', 180)) / 2
        
        self.history.append({
            'knee': avg_knee,
            'elbow': avg_elbow,
            'hip': avg_hip
        })
        
        if len(self.history) > self.window_size:
            self.history.pop(0)
        
        if len(self.history) < 10:
            return 'detecting', 0.0
        
        knee_avg = np.mean([h['knee'] for h in self.history])
        elbow_avg = np.mean([h['elbow'] for h in self.history])
        hip_avg = np.mean([h['hip'] for h in self.history])
        
        knee_var = np.var([h['knee'] for h in self.history])
        elbow_var = np.var([h['elbow'] for h in self.history])
        
        scores = {
            'squat': self._check_squat(knee_avg, knee_var, hip_avg, elbow_avg),
            'pushup': self._check_pushup(elbow_avg, elbow_var, hip_avg, knee_avg),
            'plank': self._check_plank(hip_avg, elbow_avg, knee_avg, elbow_var, knee_var)
        }
        
        detected_exercise = max(scores, key=scores.get)
        confidence = scores[detected_exercise]
        
        return detected_exercise, confidence
    
    def _check_squat(self, knee_avg, knee_var, hip_avg, elbow_avg):
        score = 0.0
        
        if knee_var > 200:
            score += 0.4
        
        if 100 < knee_avg < 160:
            score += 0.3
        
        if elbow_avg > 150:
            score += 0.2
        
        if 120 < hip_avg < 170:
            score += 0.1
        
        return score
    
    def _check_pushup(self, elbow_avg, elbow_var, hip_avg, knee_avg):
        score = 0.0
        
        if elbow_var > 200:
            score += 0.4
        
        if 90 < elbow_avg < 150:
            score += 0.3
        
        if 150 < hip_avg < 190:
            score += 0.2
        
        if knee_avg > 160:
            score += 0.1
        
        return score
    
    def _check_plank(self, hip_avg, elbow_avg, knee_avg, elbow_var, knee_var):
        score = 0.0
        
        if elbow_var < 50 and knee_var < 50:
            score += 0.4
        
        if 160 < hip_avg < 190:
            score += 0.3
        
        if 70 < elbow_avg < 110:
            score += 0.2
        
        if knee_avg > 160:
            score += 0.1
        
        return score
    
    def reset(self):
        self.history = []