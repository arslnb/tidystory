from app import app
from configs import production as config
from flask import render_template
from flask_login import current_user
from flask_login import login_required
from firebase_admin import db
from flask import abort
from flask import redirect
from flask import url_for
from flask import request
from flask import make_response
from sessions import User
import datetime

from app.methods import unroll as u
from app import apiTwitter

@app.route('/test')
def testRoute():
    # payload = {
    #     "author_name": "Arsalan Bashir",
    #     "author_handle": "arslnb",
    #     "tweet_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    #     "uid": "akjsdna"
    # }
    # u.getTimelineImg(payload)
    print apiTwitter.GetStatus(1050015903247667200)
    apiTwitter.PostUpdate("@arsalanbashir Hello, Arsalan! Here it is!", in_reply_to_status_id=1050015903247667200)
    return "ok"
    # return "Done"

# * HOME PAGE AND DASHBOARD
@app.route('/')
def home():
    if current_user.is_authenticated:
        storms = db.reference('tweetstorms').order_by_child('unrolled_by_uid').equal_to(current_user.id).get()
        collections = db.reference('collections').order_by_child('author_uid').equal_to(current_user.id).get()
        featured = db.reference('featured').get()
        return render_template('private/home.html', user = current_user, 
            title = "Home - ", storms = storms, collections = collections,
            featured = featured)
    else:
        storms = db.reference('tweetstorms').order_by_child('timestamp').limit_to_last(5).get()
        collections = db.reference('collections').order_by_child('time').limit_to_last(4).get()
        active = db.reference('tweetstorms').order_by_child('totalAnnotations').limit_to_last(3).get()
        featured = db.reference('featured').get()
        return render_template('public/landing.html', storms = storms, collections = collections,
            featured = featured, active = active)

# * COLLECTIONS
# Display collections using long link
@app.route('/collection/<uid>')
def collection(uid):
    if current_user.is_authenticated:
        collection = db.reference('collections/' + str(uid)).get()
        if collection:
            return render_template('private/collection.html', user = current_user, 
                collection = collection, adminId = config.adminId)
        else:
            abort(404)
    else:
        collection = db.reference('collections/' + str(uid)).get()
        if collection:
            return render_template('public/collection.html', collection = collection)
        else:
            abort(404)

# Display collections using long link
@app.route('/c/<sId>')
def showShortCollection(sId):
    _c = db.reference('collections/').order_by_child('shortCode').equal_to(sId).get()
    if _c:
        collection = _c.values()[0]
        if current_user.is_authenticated:
            return render_template('private/collection.html', user = current_user, 
                collection = collection, adminId = config.adminId)
        else:
            return render_template('public/collection.html', collection = collection)
    else:
        abort(404)

# * STORIES
# Display stories using long link
@app.route('/storm/<uid>')
def showStorm(uid):
    if current_user.is_authenticated:
        storm = db.reference('tweetstorms/' + str(uid)).get()
        if storm:
            collections = db.reference('collections').order_by_child('author_uid').equal_to(current_user.id).get()
            return render_template('private/storm.html', storm = storm, 
                user = current_user, storm_id = uid, collections = collections)
        else:
            abort(404)
    else:
        storm = db.reference('tweetstorms/' + str(uid)).get()
        if storm:
            return render_template('public/storm.html', storm = storm,
                storm_id = uid)
        else:
            abort(404)

# Display story using short link
@app.route('/s/<sId>')
def showShortStorm(sId):
    _s = db.reference('tweetstorms/').order_by_child('shortCode').equal_to(sId).get()
    if _s:
        storm = _s.values()[0]
        uid = storm['story_id']
        if current_user.is_authenticated:
            collections = db.reference('collections').order_by_child('author_uid').equal_to(current_user.id).get()
            return render_template('private/storm.html', storm = storm, 
                user = current_user, storm_id = uid, collections = collections)
        else:
            return render_template('public/storm.html', storm = storm,
                storm_id = uid)
    else:
        abort(404)

# * DISCOVER PAGE
@app.route('/discover')
def discover():
    if current_user.is_authenticated:
        storms = db.reference('tweetstorms').order_by_child('timestamp').limit_to_last(5).get()
        collections = db.reference('collections').order_by_child('time').limit_to_last(4).get()
        active = db.reference('tweetstorms').order_by_child('totalAnnotations').limit_to_last(3).get()
        featured = db.reference('featured').get()
        return render_template('private/discover.html', storms = storms, collections = collections,
            featured = featured, active = active, user = current_user)
    else:
        return redirect(url_for('home'))

@app.route('/search')
def searchResults():
    keyword = request.args.get('q')
    # ! This needs some doing. Search is really crap at the minute. 
    # ! Probably should use elasticsearch or something. Or even algolia. 
    stories = db.reference('tweetstorms').order_by_child('master_tweet/text').start_at(keyword).end_at(keyword+"\uf8ff").get()
    collections = db.reference('collections').order_by_child('title').start_at(keyword).end_at(keyword+"\uf8ff").get()
    if current_user.is_authenticated:
        return render_template('private/search.html', user = current_user, 
            storms = stories, keyword = keyword, collections = collections, 
            title = "Search - ")
    else:
        return render_template('public/search.html', storms = stories, 
            collections = collections, keyword = keyword, title = "Search - ")

# * GENERATE STATIC SITEMAP.XML FILE
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    try:
        pages=[]
        ten_days_ago=(datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()

        stories = db.reference('tweetstorms').order_by_child('is_ready').equal_to(True).get()
        collections = db.reference('collections').get()
        for story in stories:
            url= "https://tidystory.com/story/" + stories[story]['story_id']
            modified_time=ten_days_ago
            pages.append([url,modified_time]) 

        for col in collections.values():
            url= "https://tidystory.com/collection/" + col['collection_id']
            modified_time=ten_days_ago
            pages.append([url,modified_time]) 

        sitemap_xml = render_template('sitemap.xml', pages=pages)
        response= make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"    
        return response
    except Exception as e:
        return(str(e))	  

# * REQURIED PAGES, SELF EXPLANATORY
@app.errorhandler(404)
def page_not_found(e):
    return render_template('public/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('public/500.html'), 500

@app.route('/privacy')
def showPrivacy():
    return render_template('public/privacy.html')

@app.route('/terms')
def showTerms():
    return render_template('public/tos.html')