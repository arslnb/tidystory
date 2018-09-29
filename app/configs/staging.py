import os

current_dir = os.path.dirname(os.path.realpath(__file__))

firebase = {
    "apiKey": "AIzaSyBXBII6ZqX0jfmgDqebsFoZtaTYuZ2nW7s",
    "authDomain": "tidystory-6c535.firebaseapp.com",
    "databaseURL": "https://tidystory-6c535.firebaseio.com",
    "projectId": "tidystory-6c535",
    "storageBucket": "tidystory-6c535.appspot.com",
    "messagingSenderId": "607573635878",
    "serviceAccount": current_dir + "/service.json",
    "databaseAuthVariableOverride": {
        "uid": "f1ffbfc198468df4a68d6bd9d5a46f97"
    }
}

# {
#   "rules": {
#     ".read": "auth != null || auth.uid == 'node-server'",
#     ".write": "auth != null || auth.uid == 'node-server'"
#   }
# }

metaBase = {
    "img": current_dir + "/meta.png",
    "collectionTag": current_dir + "/tag.png",
    "font1": current_dir + "/f1.ttf",
    "font2": current_dir + "/f2.ttf",
    "font3": current_dir + "/f3.ttf"
}

appKey = "some-insanely-long-key"
adminId = "BtDNKZ9zI5ZsnkLbVGbVczQzcpi1"

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