import datetime
import pickle

import bbox as bbox
import cv2
import os


import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate(r"C:\Users\Pooja Joshi\Desktop\attendence_system\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
     'databaseURL': "https://faceattendencerealtime-39d59-default-rtdb.firebaseio.com/",
     'storageBucket': "faceattendencerealtime-39d59.appspot.com"
})

bucket  =  storage.bucket()
# videotape height and width
cap=cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread(r"C:\Users\Pooja Joshi\Desktop\attendence_system\Resources\background.png")

# importing the mode images in list

folderModePath=r"C:\Users\Pooja Joshi\Desktop\attendence_system\Resources\Modes"
modePathList=os.listdir(folderModePath)
imgModeList=[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

print(len(imgModeList))  # tells no of images in modes


#load the encoding file

file=open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

#  which mode to be opened
modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img=cap.read()

    # make the size of image small
    imgs=cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

    # detect faces in current frame and encodings of the frame
    faceCurFrame=face_recognition.face_locations(imgs)
    # encoding of the current face
    encodeCurFrame =face_recognition.face_encodings(imgs,faceCurFrame)
    # is responsible for replacing a portion of the imgBackground image with the contents of the img image
    imgBackground[162:162+480, 55:55+640]=img
    # used to replace a specific region in the imgBackground image with the content from imgModeList[0]
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

     # matching the encodings of current face and stored one
    if faceCurFrame:
        for encodeFace, faceloc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            # print("matches", matches)
            # print("facedis", faceDis)

            matchIndex = np.argmin(faceDis)
            #  print("Mtch Index", matchIndex)

            # print("Knownn face was detected")
            # print(studentIds[matchIndex])
            if matches[matchIndex]:
                # for giving green rectangle at face
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                # student information is stored
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading",(275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    counter = 1
                    modeType = 1

        if counter!= 0:
            if counter ==1:
                studentInfo = db.reference(f'Students/{id}').get()  # download all the information of particular id
                print(studentInfo)
                # get the image from the stoarge
                blob = bucket.get_blob(fr"C:\Users\Pooja Joshi\Desktop\attendence_system\images/{id}.jpg")
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendence_time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed=(datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:

                    ref=db.reference(f'Students/{id}')
                    studentInfo['total_attendence'] += 1
                    ref.child('total_attendence').set(studentInfo['total_attendence'])
                    ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType !=3:
                if 10<counter<20:
                    modeType = 2


                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter<=10 :

                    cv2.putText(imgBackground, str(studentInfo['total_attendence']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 655),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
            counter += 1


            if counter>=20:
                counter=0
                modeType=0
                studentInfo=[]
                imgStudent=[]
                imgBackground[44:44 + 633, 808:808 + 414] =  imgModeList[modeType]
    else:
       modeType =0
       counter = 0

    # cv2.imshow("Webcam", img)
    # used to display an image and outer boundary of that image
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(5)
