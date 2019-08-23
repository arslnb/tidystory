import os

current_dir = os.path.dirname(os.path.realpath(__file__))

firebase = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "serviceAccount": current_dir + "/service.json",
    "databaseAuthVariableOverride": {
        "uid": ""
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

appKey = ""
adminId = ""
hashSalt = ""

twitter = {
    "consumerKey": "",
    "consumerSecret": "",
    "accessKey": "",
    "accessSecret": ""
}

cloudinary = {
    "name": "",
    "key": "",
    "secret": ""
}

lp = {
    "key": ""
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
