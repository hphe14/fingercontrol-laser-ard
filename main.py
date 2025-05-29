import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence = 0.8, min_tracking_confidence = 0.5,  max_num_hands = 1) as hands:

    #Cam Feed
    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
        
        image_height, image_width = image.shape[:2]  
        midp_x , midp_y = image_width/2, image_height/2
        
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                index_x = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width
                index_y = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height
                
                #relative to middle of camera
                #rel_x, rel_y = (index_x - midp_x), (midp_y - index_y)
                #print(rel_x)
                
                
                #limit to 0 - 180
                downscale_x = index_x * 180 / image_width
                downscale_y = index_y * 180 / image_height
                print(downscale_y)
                
                
                #draw hand landmarks and connections
                mp_drawing.draw_landmarks(
                    image, 
                    hand, 
                    mp_hands.HAND_CONNECTIONS)
            
        cv2.imshow('cam',image)
        
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()