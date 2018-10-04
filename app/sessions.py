from app import app
from app import login_manager
from app.configs import production as config
from flask_login import UserMixin
from flask_login import login_user
from flask_login import logout_user
from firebase_admin import db
from firebase_admin import auth
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
from flask import url_for
from app import apiTwitter

class User(UserMixin):
    def __init__(self, uid, displayName, email, photoURL, userData):
        super(User, self).__init__()
        self.id = unicode(uid)
        self.displayName = displayName
        self.email = email
        self.photoURL = photoURL
        self.userData = userData
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

@login_manager.user_loader
def load_user(user_id):
    _r = db.reference('user_profiles/' + str(user_id)).get()
    if _r:
        if not "photoURL" in _r.keys():
            _r['photoURL'] = '/static/img/default.png'
        if not "email" in _r.keys():
            _r['email'] = 'unverified_email'
        return User(_r['uid'], _r['displayName'], _r['email'], _r['photoURL'], _r)
    else:
        return None

@app.route('/v1/user', methods=["POST"])
def user_sessions():
    data = request.get_json(force = True)
    try:
        auth.verify_id_token(data['id_token'], check_revoked=True)
        _u = data['user']
        user = db.reference('user_profiles/' + _u['uid']).get()
        if user:
            userObj = User(user['uid'], user['displayName'], user['email'], 
                    user['photoURL'], user)
            login_user(userObj)
        else:
            _uData = _u['providerData'][0]

            if not _uData['email']:
                _uData['email'] = False

            if not _uData['photoURL']:
                _uData['photoURL'] = "/static/img/default.png"

            if not _uData['displayName']: 
                _uData['displayName'] = False

            if data['grant_type'] == "password":
                tw_handle = False
                tw_uid = False
                _uData['displayName'] = _uData['email'].split('@')[0]
            else:
                tw_handle = apiTwitter.GetUser(_uData['uid']).AsDict()['screen_name']
                tw_uid = _uData['uid']

            db.reference('user_profiles/' + _u['uid']).set({
                'uid': _u['uid'], 
                'email': _uData['email'], 
                'displayName': _uData['displayName'], 
                'photoURL': _uData['photoURL'],
                'tw_uid': tw_uid,
                'tw_handle': tw_handle
            })

            _nu = db.reference('user_profiles/' + _u['uid']).get()

            userObj = User(_u['uid'], _uData['displayName'], _uData['email'], 
                    _uData['photoURL'], _nu)
            login_user(userObj)
        return jsonify({'status': 'success'})
    except ValueError:
        return jsonify({'status': 'error', 'message': 'invalid token provided'})
    except auth.AuthError:
        return jsonify({'status': 'error', 'message': 'failed to validate token'})

@app.route('/signin')
def login():
    return render_template('public/signin.html', title="Sign In - ")

@app.route('/signup')
def signup():
    return render_template('public/signup.html', title="Sign Up - ")

@app.route('/reset')
def reset():
    return render_template('public/reset.html', title="Reset Password - ")

@app.route('/signout')
def signout():
    logout_user()
    return redirect(url_for('home'))
