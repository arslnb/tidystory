import os

current_dir = os.path.dirname(os.path.realpath(__file__))

firebase = {
    "apiKey": "AIzaSyAUP6XIt5WlkBa7T4bv-lpr9ievs-BDoEM",
    "authDomain": "tidystory-staging.firebaseapp.com",
    "databaseURL": "https://tidystory-staging.firebaseio.com",
    "projectId": "tidystory-staging",
    "storageBucket": "tidystory-staging.appspot.com",
    "messagingSenderId": "642137131574",
    "serviceAccount": current_dir + "/staging.json",
    "databaseAuthVariableOverride": {
        "uid": "f1ffbfc198468df4a68d6bd9d5a46f97"
    }
}

metaBase = {
    "img": current_dir + "/meta.png",
    "collectionTag": current_dir + "/tag.png",
    "timelineBase": current_dir + "/timeline.png",
    "font1": current_dir + "/f1.ttf",
    "font2": current_dir + "/f2.ttf",
    "font3": current_dir + "/f3.ttf"
}

appKey = "some-insanely-long-key"
adminId = "BtDNKZ9zI5ZsnkLbVGbVczQzcpi1"
hashSalt = "El3fkRIo3"

twitter = {
    "consumerKey": "fZ5MWwrTEuzK7aX2esvdsRc8f",
    "consumerSecret": "16xrEzRf0RZJVELNx3pw6ZbeqVCM4cwUUBBa79P7HtlFq6LstQ",
    "accessKey": "1046292893550473216-gJALXlEFEtiVTKIYdolifPTufcZXxJ",
    "accessSecret": "blZLjo580KyE7hkasHNVFZrvAQlFm37TRqrgFnKD8BFHG"
}

cloudinary = {
    "name": "tidystory",
    "key": "929736318553763",
    "secret": "2DU6OC9SvRTIsD242Lc0ihHKdbU" 
}

lp = {
    "key": "5b6f49d2413603efcdd8c4998017c9578b28a059f72e4"
}

composer = {
    "greetings": [
        "Hey! ", "Hola! ", "Hi! ", "What's up? ", "Yo, ", "Hello! ", "Sup! ", "G'day! ", "Salut! ", "What's up? "
    ],
    "body": [
        "Here's the story you requested. Have a nice one \n\n https://tidystory.com/s/",
        "Hope you're excited to check out the story by __auth_handle__ that you requested. Here it is \n\n https://tidystory.com/s/",
        "The story by __auth_handle__ is ready for you to read. Check it out here \n\n https://tidystory.com/s/",
        "You can read this story over here: \n\n https://tidystory.com/s/",
        "Here's that story by __auth_handle__ you wanted: \n\n https://tidystory.com/s/",
    ]
}