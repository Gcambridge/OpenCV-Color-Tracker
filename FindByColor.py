import cv2
import numpy as np
import math
from decimal import Decimal

cap = cv2.VideoCapture(0)

#Lower color limit for yellow: 
lower_color = np.array([27, 100, 100])
#Upper color limit for yellow
upper_color = np.array([47,255,255])

while True:
  _, frame = cap.read()

  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  height = np.size(frame, 0)
  width = np.size(frame, 1)

  centerX = width/2
  centerY = height/2

  cv2.line(frame,(int(width/2) ,0),(int(width/2), 3 * int(height/8) ),(255,255,255),3) #line top center to box
  cv2.line(frame,(int(width/2) ,height),(int(width/2), 5 * int(height/8) ),(255,255,255),3) #line bottom center to box
  cv2.line(frame,(0,int(height/2)),(3 * int(width/8), int(height/2)),(255,255,255),3) #line left center to box
  cv2.line(frame,(width,int(height/2)),(5 * int(width/8), int(height/2)),(255,255,255),3) #line right center to box

  mask = cv2.inRange(hsv, lower_color, upper_color)
  im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
  biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
  x,y,w,h = cv2.boundingRect(biggest_contour)
  cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

  cirX = int((x+(x+w))/2)
  cirY = int((y+(y+h))/2)

  cv2.circle(frame, (cirX, cirY), 10, (255,0,0), -1)
  
  cv2.line(frame,(int(width/2), int(height/2)),(cirX,cirY),(0,255,0),3)

  xErrorPercent = round(Decimal((cirX - centerX) / ((width/2)-10)), 2)
  yErrorPercent = round(Decimal((centerY - cirY) / ((height/2)-10)), 2)

  cv2.rectangle(frame,(0, height), (450,int(height - 75)), (0,0,0), -1)

  cv2.putText(frame,'X Error Percent: ' + str(xErrorPercent),
  (5,height-55), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,255), 1, cv2.LINE_AA)

  cv2.putText(frame,' Y Error Percent: ' + str(yErrorPercent),
  (185,height-55), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,255,0), 1, cv2.LINE_AA)

  maxSpeed = 1325
  minSpeed = 1131
  rangeToMap = maxSpeed - minSpeed

  curve = int(xErrorPercent * rangeToMap)
  throttle = int(yErrorPercent * rangeToMap) + minSpeed

  leftMotorSpeed = throttle
  rightMotorSpeed = throttle 
  found = False

  green = 0 
  red = 255
  cv2.rectangle(frame, ( 3 * int(width/8) , 5 * int(height/8) ), ( 5 * int(width/8), 3 * int(height/8) ), (0, green , red), 3)

  if abs(xErrorPercent) < .22 and abs(yErrorPercent) < .20:
    green = 255
    red = 0
    found = True
    capture = True

    if found and capture:
      cv2.imwrite('capture.png' , frame)
      capture = False
    #found box
    cv2.rectangle(frame, ( 3 * int(width/8) , 5 * int(height/8) ), ( 5 * int(width/8), 3 * int(height/8) ), (0, green , red), 3)
    
  elif throttle <= minSpeed:
    throttle = 0
    if curve < 0:
      rightMotorSpeed = maxSpeed
      leftMotorSpeed = 0
    elif curve > 0:
      leftMotorSpeed = maxSpeed
      rightMotorSpeed = 0 

  elif curve > 0:
    rightMotorSpeed = throttle - curve

  elif curve < 0:
    leftMotorSpeed = throttle + curve

  motorDiff = abs(rightMotorSpeed - leftMotorSpeed)

  cv2.putText(frame,'Curve: ' + str(curve)  + ' Throttle: ' + str(throttle) + '        Found: ' + str(found) ,
  (5,height-35), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)

  cv2.putText(frame, 'Left Motor: ' + str(leftMotorSpeed) + ' Right Motor: ' + str(rightMotorSpeed) + ' motorDiff: ' + str(motorDiff),
  (5,height-10), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)

  cv2.imshow('show color', frame)
  

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break
    
cap.release()
cv2.destroyAllWindows()
