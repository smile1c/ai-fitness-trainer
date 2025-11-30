"""
Demo script for TensorFlow Hub Exercise Recognition - 20 Exercises
"""

import cv2
from models.tfhub_recognizer import TFHubExerciseRecognizer
from models.exercise_analyzer import ExerciseAnalyzer

def select_exercise():
    """Let user select exercise"""
    print("\n" + "="*70)
    print("📝 Select Exercise Type (เลือกท่าออกกำลังกาย):")
    print("="*70)
    
    exercises = {
        '1': ('squat', '🏋️  Squat / สควอท'),
        '2': ('pushup', '💪 Push-up / วิดพื้น'),
        '3': ('plank', '🧘 Plank / แพลงค์'),
        '4': ('lunges', '🦵 Lunges / ลันจ์'),
        '5': ('jumping_jacks', '🤸 Jumping Jacks / กระโดดแจ็ค'),
        '6': ('situp', '🔄 Sit-up / ซิทอัพ'),
        '7': ('high_knees', '🏃 High Knees / ยกเข่าสูง'),
        '8': ('burpees', '💥 Burpees / เบอร์ปี้'),
        '9': ('mountain_climbers', '⛰️  Mountain Climbers / ปีนเขา'),
        '10': ('side_plank', '↔️  Side Plank / แพลงค์ข้าง'),
        '11': ('running', '🏃‍♂️ Running in Place / วิ่งหน้าที่'),
        '12': ('crunches', '💪 Crunches / ครunch'),
        '13': ('leg_raises', '🦵 Leg Raises / ยกขา'),
        '14': ('bicycle_crunches', '🚴 Bicycle Crunches / ปั่นจักรยาน'),
        '15': ('standing_knee_raises', '🦵 Standing Knee Raises / ยกเข่ายืน'),
        '16': ('wall_sit', '🧱 Wall Sit / นั่งพิงกำแพง'),
        '17': ('glute_bridge', '🍑 Glute Bridge / ยกสะโพก'),
        '18': ('jumping', '⬆️  Jumping / กระโดด'),
        '19': ('star_jumps', '⭐ Star Jumps / กระโดดดาว'),
        '20': ('squat_jumps', '💥 Squat Jumps / สควอทกระโดด'),
        '0': ('auto', '🤖 Auto-Detect (AI) / ตรวจจับอัตโนมัติ')
    }
    
    for key, (_, name) in sorted(exercises.items()):
        print(f"  {key:>2}. {name}")
    
    print("="*70)
    
    while True:
        choice = input("\nEnter choice (0-20): ").strip()
        if choice in exercises:
            exercise_id, exercise_name = exercises[choice]
            print(f"\n✅ Selected: {exercise_name}")
            return exercise_id
        else:
            print("❌ Invalid! Enter 0-20")

def main():
    print("=" * 70)
    print("💪 AI FITNESS TRAINER - 20 EXERCISES")
    print("=" * 70)
    
    selected_exercise = select_exercise()
    
    print("\n🎥 Starting webcam...")
    print("\n📝 Instructions:")
    print("   - Stand 2-3 meters from camera")
    print("   - Keep full body visible")
    print("   - Press 'q' to quit")
    print("   - Press 'r' to reset counter")
    print("   - Press 'c' to change exercise")
    print("=" * 70)
    
    print("\nLoading TensorFlow Hub MoveNet...")
    recognizer = TFHubExerciseRecognizer()
    analyzer = ExerciseAnalyzer(exercise_type=selected_exercise)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Cannot open webcam")
        return
    
    print("✅ Webcam ready!\n")
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if selected_exercise == 'auto':
            exercise, confidence, keypoints, angles = recognizer.detect_exercise(frame)
            feedback, _ = analyzer.analyze_frame(angles, detected_exercise=exercise, confidence=confidence)
        else:
            exercise, confidence, keypoints, angles = recognizer.detect_exercise(frame)
            if keypoints is not None and angles:
                feedback, _ = analyzer.analyze_frame(angles, detected_exercise=selected_exercise, confidence=1.0)
            else:
                feedback = {"error": "No pose"}
        
        if keypoints is not None:
            frame = recognizer.draw_keypoints(frame, keypoints)
            
            h, w = frame.shape[:2]
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 250), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            y_offset = 40
            
            if selected_exercise != 'auto':
                exercise_names = {
                    'squat': 'Squat / สควอท',
                    'pushup': 'Push-up / วิดพื้น',
                    'plank': 'Plank / แพลงค์',
                    'lunges': 'Lunges / ลันจ์',
                    'jumping_jacks': 'Jumping Jacks / กระโดดแจ็ค',
                    'situp': 'Sit-up / ซิทอัพ',
                    'high_knees': 'High Knees / ยกเข่าสูง',
                    'burpees': 'Burpees / เบอร์ปี้',
                    'mountain_climbers': 'Mountain Climbers / ปีนเขา',
                    'side_plank': 'Side Plank / แพลงค์ข้าง',
                    'running': 'Running / วิ่งหน้าที่',
                    'crunches': 'Crunches / ครunch',
                    'leg_raises': 'Leg Raises / ยกขา',
                    'bicycle_crunches': 'Bicycle Crunches / ปั่น',
                    'standing_knee_raises': 'Knee Raises / ยกเข่า',
                    'wall_sit': 'Wall Sit / นั่งพิง',
                    'glute_bridge': 'Glute Bridge / ยกสะโพก',
                    'jumping': 'Jumping / กระโดด',
                    'star_jumps': 'Star Jumps / กระโดดดาว',
                    'squat_jumps': 'Squat Jumps / สควอทกระโดด'
                }
                name = exercise_names.get(selected_exercise, selected_exercise)
                cv2.putText(frame, name, (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 3, cv2.LINE_AA)
                y_offset += 50
            elif 'detected' in feedback:
                cv2.putText(frame, feedback['detected'], (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2, cv2.LINE_AA)
                y_offset += 50
            
            for key, message in feedback.items():
                if key in ['detected', 'reps']:
                    continue
                
                if "Perfect" in message or "Good" in message:
                    color = (0, 255, 0)
                elif "Unknown" in message:
                    color = (0, 165, 255)
                else:
                    color = (0, 0, 255)
                
                cv2.putText(frame, message, (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
                y_offset += 35
            
            if 'reps' in feedback:
                cv2.putText(frame, feedback['reps'], (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        else:
            cv2.putText(frame, "No pose detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('AI Fitness - Q:quit R:reset C:change', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('r'):
            analyzer.reset_counter()
            print("🔄 Counter reset!")
        elif key == ord('c'):
            cap.release()
            cv2.destroyAllWindows()
            selected_exercise = select_exercise()
            analyzer = ExerciseAnalyzer(exercise_type=selected_exercise)
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 70)
    print(f"📊 Results:")
    print(f"   Exercise: {selected_exercise}")
    print(f"   Reps: {analyzer.rep_count}")
    print("✅ Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()