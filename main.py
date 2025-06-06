import cv2
import mediapipe as mp
import serial.tools.list_ports
import math


mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


fingers = {
    "thumb" : [1,2,3,4],    
    "index" : [5,6,7,8],    
    "middle" : [9,10,11,12],  
    "ring" : [13,14,15,16],    
    "pinky" : [17,18,19,20]    
}


cap = cv2.VideoCapture(0)
cam_width, cam_height = 640, 480
mid_x , mid_y = int(cam_width/2), int(cam_height/2)

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
text_color = (0, 0, 255)
text_thickness = 2
offset = 10


port = serial.tools.list_ports.comports()
com_port = 'None'
default_msg = f'{90},{90},{0}\n'

for i in range (0, len(port)):
    port_name = str(port[i])
    if 'Arduino' in port_name:
        com_port = port_name.split(' ')[0]
       
if com_port != 'None':
    ser = serial.Serial(com_port, 9600)
    print(f'connected to {com_port}')
else:
    print("No Arduino Connected")
    
    
def calc_distance(pointA,pointB,pointC):
    ax,ay = pointA
    bx,by = pointB
    cx,cy = pointC
   
    distance_AB =  math.sqrt((bx-ax)**2 + (by-ay)**2)
    distance_AC =  math.sqrt((cx-ax)**2 + (cy-ay)**2)
    #print(distance)
    
    return distance_AB,distance_AC

def calc_gradient(pointA, pointB):
    x1,y1 = pointA
    x2,y2 = pointB
    deltax = (x2 - x1)
    deltay = (y2 - y1)
      
    try:
        gradient = (deltay) / (deltax)
    except ZeroDivisionError:
        return 0
    #c = (y1 - (gradient*x1))
        
    return gradient
    
def find_finger_pos(finger: str, joint: int ):
    current_finger = fingers[finger]
    finger_pos_x = int(hand.landmark[current_finger[joint-1]].x * cam_width)
    finger_pos_y = int(hand.landmark[current_finger[joint-1]].y * cam_height)
    
    text_offset_x = finger_pos_x + offset
    text_offset_y = finger_pos_y - offset
    
    (text_w, text_h), baseLine = cv2.getTextSize(f'{(finger_pos_x,finger_pos_y)}', font, font_scale, text_thickness)
    
    text_offset_x = max(0, min(text_offset_x, cam_width - text_w))  
    text_offset_y = max(text_h, min(text_offset_y, cam_height - text_h)) 
    
    
    #cv2.circle(image, (finger_pos_x,finger_pos_y), radius=6, thickness=5, color=(0,200,255))
    #cv2.putText(image, f'{(finger_pos_x,finger_pos_y)}', (text_offset_x,text_offset_y), font, font_scale, text_color, text_thickness)
    
    return finger_pos_x,finger_pos_y


def check_fist():
    check_fing =[]

    wrist_x = int(hand.landmark[0].x * cam_width)
    wrist_y = int(hand.landmark[0].y * cam_height)
    
    #ignoring thumb because why not. Not really a fist then but close enough
    
    #thumb_cmc_x,thumb_cmc_y = find_finger_pos("thumb",2)
    #thumb_tip_x,thumb_tip_y = find_finger_pos("thumb",4)
    
    for i in list(fingers)[1:]:
        mcp_x, mcp_y = find_finger_pos(i,1)
        tip_x, tip_y = find_finger_pos(i,4)
             
        distance_AB, distance_AC = calc_distance((wrist_x,wrist_y),(mcp_x,mcp_y),(tip_x,tip_y))
        #distance_thumb_A, distance_thumb_B = calc_distance((wrist_x,wrist_y),(thumb_cmc_x,thumb_cmc_y),(thumb_tip_x,thumb_tip_y))
        
        #still triggers if palm is tilted down but for not good enough
        if distance_AC < distance_AB:
            check_fing.append(1)
            
        #if distance_thumb_B < distance_thumb_A:
            #check_fing.append(1)
        
    print(check_fing)
       
           
    fing_count = check_fing.count(1)
    if fing_count == 4:
        return 1
    else:
        return 0
    
   
def hand_angle():
    mcp_avg_x = 0
    mcp_avg_y = 0
    
    wrist_x = int(hand.landmark[0].x * cam_width)
    wrist_y = int(hand.landmark[0].y * cam_height)
  
    for i in list(fingers)[1:]:
        x, y = find_finger_pos(i,1)
        mcp_avg_x += x/4
        mcp_avg_y += y/4
        
        
    gradient = calc_gradient((wrist_x,wrist_y),(mcp_avg_x,mcp_avg_y))
    #print(gradient *-1)
    
    #Calculate and Display the actual hand angle from 0-360 degrees clockwise.
    if wrist_x > mcp_avg_x:
        angle = 270 + (math.degrees(math.atan(gradient))) 
    else:
        angle = 90 + (math.degrees(math.atan(gradient)))

    
    cv2.putText(image, f'{int(angle)}', (340,220), font, font_scale, text_color, text_thickness)
 
    # to draw the hand line with correct gradient and with its origin centered in the middle of the screen
    hand_line_y1 = int(gradient * (0 - mid_x) + mid_y)  
    hand_line_y2 = int(gradient * (cam_width - mid_x) + mid_y)
    cv2.line(image,(0,hand_line_y1),(cam_width,hand_line_y2),(0, 0, 255), 2) 
  
    #cv2.circle(image, (int(mcp_avg_x),int(mcp_avg_y)), radius=6, thickness=5, color=(0,200,255))
    #cv2.circle(image, (wrist_x,wrist_y), radius=6, thickness=5, color=(0,200,255))
    
    cv2.line(image,(mid_x,0),(mid_x,cam_width),(0, 0, 255) , 2) # line to cut middle
    cv2.circle(image, (mid_x,mid_y), radius=6, thickness=5, color=(0,200,255)) #midpoint visual
    
    return
    

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
                
                if check_fist() == 0:
                    index_pos_x, index_pos_y = find_finger_pos('index', 4)
                    servo_pos_x,servo_pos_y = servo_control(index_pos_x, index_pos_y)              
                    full_message = f'{servo_pos_x},{servo_pos_y},{1}\n'
                    ser.write(full_message.encode())
                else:
                    ser.write(default_msg.encode())
                    
                    
                hand_angle()
                
                   
                    
                #draw hand landmarks and connections
                mp_drawing.draw_landmarks(
                    image, 
                    hand, 
                    mp_hands.HAND_CONNECTIONS,
                    )
        else:
            ser.write(default_msg.encode())
            
               
        cv2.imshow('cam',image)
        if cv2.waitKey(1) == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()