import cv2
import mediapipe as mp
import serial.tools.list_ports


mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


finger_tips = {
    "thumb" : 4,    #mp_hands.HandLandmark.THUMB_TIP
    "index" : 8,    #mp_hands.HandLandmark.INDEX_FINGER_TIP
    "middle" : 12,  #mp_hands.HandLandmark.MIDDLE_FINGER_TIP
    "ring" : 16,    #mp_hands.HandLandmark.RING_FINGER_TIP
    "pinky" : 20    #mp_hands.HandLandmark.PINKY_TIP
}


cap = cv2.VideoCapture(0)
cam_width, cam_height = 640, 480

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.75
text_color = (0, 0, 255)
text_thickness = 2
offset = 10


port = serial.tools.list_ports.comports()
com_port = 'None'

for i in range (0, len(port)):
    port_name = str(port[i])
    if 'Arduino' in port_name:
        com_port = port_name.split(' ')[0]
       
if com_port != 'None':
    ser = serial.Serial(com_port, 9600)
    print(f'connected to {com_port}')
else:
    print("No Arduino Connected")
    
    
def finger_tip_pos(hand_landmark, finger):
    finger_tip_ind = finger_tips[finger]
    finger_pos_x = int(hand_landmark.landmark[finger_tip_ind].x * cam_width)
    finger_pos_y = int(hand_landmark.landmark[finger_tip_ind].y * cam_height)
    
    text_offset_x = finger_pos_x + offset
    text_offset_y = finger_pos_y - offset
    
    (text_w, text_h), baseLine = cv2.getTextSize(f'{(finger_pos_x,finger_pos_y)}', font, font_scale, text_thickness)
    
    text_offset_x = max(0, min(text_offset_x, cam_width - text_w))  
    text_offset_y = max(text_h, min(text_offset_y, cam_height - text_h)) 
    
    
    cv2.circle(image, (finger_pos_x,finger_pos_y), radius=6, thickness=5, color=(0,200,255))
    cv2.putText(image, f'{(finger_pos_x,finger_pos_y)}', (text_offset_x,text_offset_y), font, font_scale, text_color, text_thickness)
    
    return finger_pos_x,finger_pos_y


def servo_control(x,y):
    #For servo control | limited to 0 - 180  
    pos_x = (180 - round(x * 180 / cam_width))  #reversing so it matches movement direction of servo
    pos_y = round(y * 180 / cam_height)

    return pos_x,pos_y


with mp_hands.Hands(min_detection_confidence = 0.8, min_tracking_confidence = 0.5,  max_num_hands = 1) as hands:
    #Cam Feed
    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        image = cv2.flip(image,1)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
        
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:

                index_pos_x, index_pos_y = finger_tip_pos(hand, "index")
                servo_pos_x,servo_pos_y = servo_control(index_pos_x, index_pos_y)              
                full_message = f'{servo_pos_x},{servo_pos_y},{1}\n'
                ser.write(full_message.encode())
                
                #draw hand landmarks and connections
                mp_drawing.draw_landmarks(
                    image, 
                    hand, 
                    mp_hands.HAND_CONNECTIONS,
                    )
        else:
            default_msg = f'{90},{90},{0}\n'
            ser.write(default_msg.encode())
            print(default_msg)
                        
        cv2.imshow('cam',image)
        if cv2.waitKey(1) == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()