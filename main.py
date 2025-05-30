import cv2
import mediapipe as mp
import serial.tools.list_ports


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)

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
                               
                #limit to 0 - 180 
                downscale_x = (180 - round(index_x * 180 / image_width))  #inverting so it matches movement direction of servo
                downscale_y = round(index_y * 180 / image_height)
                pos = f'{downscale_x},{downscale_y}\n'
                #print(pos)
                ser.write(pos.encode())
                
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