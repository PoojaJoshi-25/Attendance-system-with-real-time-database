
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate(r"C:\Users\Pooja Joshi\Desktop\attendence_system\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
     'databaseURL': "https://faceattendencerealtime-39d59-default-rtdb.firebaseio.com/"
})

# will create student directory in database that is ids
ref = db.reference('Students')

data = {
    "210121622":
        {
            "name": "Pooja Joshi",
            "major": "Student",
            "starting_year": 2017,
            "total_attendence": 6,
            "standing": "G",
            "year": 2,
            "last_attendence_time": "2022-12-11 00:54:34"
        },
"210121623":
        {
            "name": "Mahak Saxena",
            "major": "Student",
            "starting_year": 2017,
            "total_attendence": 5,
            "standing": "G",
            "year": 2,
            "last_attendence_time": "2022-12-11 00:54:34"
        },
"210111126":
        {
            "name": "Manoj Goswami",
            "major": "Student",
            "starting_year": 2017,
            "total_attendence": 8,
            "standing": "G",
            "year": 2,
            "last_attendence_time": "2022-12-11 00:54:34"
        }

}

for key,value in data.items():
    ref.child(key).set(value)