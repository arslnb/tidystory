import os

current_dir = os.path.dirname(os.path.realpath(__file__))

firebase = {
    "apiKey": "AIzaSyBXBII6ZqX0jfmgDqebsFoZtaTYuZ2nW7s",
    "authDomain": "tidystory-6c535.firebaseapp.com",
    "databaseURL": "https://tidystory-6c535.firebaseio.com",
    "projectId": "tidystory-6c535",
    "storageBucket": "tidystory-6c535.appspot.com",
    "messagingSenderId": "607573635878",
    "serviceAccount": current_dir + "/production.json",
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
    "consumerKey": "BThB1OSHSBEZTN2WN9ZIaBzjH",
    "consumerSecret": "zfU9gAVxxbwn0bAWQWuoIbTQA7Ct8PIuJcJHCMSesYLkzCfTjJ",
    "accessKey": "1005509129417326592-sAQgIqsmCoWSYVrwZXOZLracIZPw2D",
    "accessSecret": "3Ko5i1kcMmm5Y7fU1xmCY74IATUKyRylLQdJD4wkia3Mr"
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