import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate(r"C:\Users\Pooja Joshi\Desktop\attendence_system\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
     'databaseURL': "https://faceattendencerealtime-39d59-default-rtdb.firebaseio.com/",
     'storageBucket': "faceattendencerealtime-39d59.appspot.com"
})


# importing the student images

folderModePath= r"C:\Users\Pooja Joshi\Desktop\attendence_system\images"
PathList=os.listdir(folderModePath)
print(PathList)  # prints names of images
imgList=[]
studentIds=[]
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderModePath, path)))
    studentIds.append(os.path.splitext(path)[0])

    # it will create a folder name images and in that images it will add all images of student in storage database
    fileName = f'{folderModePath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

    #print(path)
    #print(os.path.splitext(path)[0])  # splits ths name and format of path like 210121622 and .png different  0 means first value

print(studentIds)

# function for encoding the images and storing them in a file
def findEncodings(imagesList):
    encodeList =[]
    for img in imagesList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # converted color
        encode=face_recognition.face_encodings(img)[0] # encoding of the image
        encodeList.append(encode)

    return encodeList
print("Encoding Started.....")
encodeListKnown = findEncodings(imgList)  # 128 bit
print(encodeListKnown)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")