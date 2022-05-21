from flask import Flask, request,jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

import cv2
import math
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils


def detectPose(image, pose):
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    height, width, _ = image.shape
    landmarks = []
    
    if results.pose_landmarks:
    
        mp_drawing.draw_landmarks(image=image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)
        for landmark in results.pose_landmarks.landmark:
            landmarks.append((int(landmark.x * width), int(landmark.y * height),
                                  (landmark.z * width)))
    
   
    return image, landmarks
    
    
def calculateAngle(landmark1, landmark2, landmark3):
  
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3
 
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    
    if angle < 0:
        angle += 360
    
    return angle


def classifyPose(landmarks, output_image):
    
    label = 'No Pose Found'
    
    left_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value])
 
    right_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value])

    
    if left_angle > 110 and left_angle < 160 and right_angle > 110 and right_angle < 160:
        label = ('Situp Down')
    elif left_angle > 200 and left_angle < 250 and right_angle > 200 and right_angle < 250:
        label = ('Situp Down')
    elif left_angle > 20 and left_angle < 90 and right_angle > 20 and right_angle < 90:
        label = ('Situp')
    elif left_angle > 260 and left_angle < 325 and right_angle > 260 and right_angle < 325:
        label = ('Situp')
    else:
        label = ('Wrong Pose')
    
    return label,left_angle,right_angle
    

@app.route('/py_server')
def index():
    return 'Running Python Flask Server'


@app.route('/situp-detection', methods=["POST"])
def detection():
    try:
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            print(filename)
            file.save('img.'+(filename.split('.')[-1]))
            image = cv2.imread('img.'+(filename.split('.')[-1]))


            output_image, landmarks = detectPose(image, pose)
            if landmarks:
                label,left_angle,right_angle = classifyPose(landmarks, output_image)
                return jsonify({'pose':label,'left-angle':int(left_angle),'right-angle':int(right_angle)})
            else:
                return 'No Pose Found'
        else:
            return 'No image attached'
    except:
        return 'Something went wrong'

if __name__ == '__main__':
    app.run()