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
    "consumerKey": "fZ5MWwrTEuzK7aX2esvdsRc8f",
    "consumerSecret": "16xrEzRf0RZJVELNx3pw6ZbeqVCM4cwUUBBa79P7HtlFq6LstQ",
    "accessKey": "1046292893550473216-pIxur8CYdwsCmHWkEkNjbN3DWi1NUI",
    "accessSecret": "Xlr4XVbkQrouhUFJyEGQWWo6WIQ4n077m1yzMXBfrbxFU"
}

cloudinary = {
    "name": "tidystory",
    "key": "929736318553763",
    "secret": "2DU6OC9SvRTIsD242Lc0ihHKdbU" 
}

lp = {
    "key": "5b6f49d2413603efcdd8c4998017c9578b28a059f72e4"
}