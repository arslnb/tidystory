from app import endpoints
from flask_restful import Resource
from flask_restful import reqparse
from flask_login import current_user
from app.methods import unroll as u
from configs import staging as config
from firebase_admin import db
from app import apiTwitter
from werkzeug import FileStorage
import datetime
import urllib
import time
import re
import os
import base64
import hashlib
import hmac
import json
import requests
from flask import request
from requests_oauthlib import OAuth1

parser = reqparse.RequestParser()
parser.add_argument('tweet_url', type=str, help='URL for Twitter Status')
parser.add_argument('lmk', type=str, help='Let-me-know email address')

class Story(Resource):
    def post(self):
        data = parser.parse_args()
        tweet_url = data['tweet_url']
        lmk = data['lmk']

        if lmk == 'false':
            lmk = False

        try:
            id_str = re.search('/status/(\d+)', tweet_url).group(1)
            tweet = apiTwitter.GetStatus(status_id=id_str).AsDict()
            now = datetime.datetime.now()
            timestamp = now.isoformat()
            vis_timestamp = now.strftime("%a, %d %b at %I:%M %p")

            storm = {
                "trigger_id": False,
                "timestamp": timestamp,
                "vis_timestamp": vis_timestamp,
                "is_ready": False,
                "totalAnnotations": 0,
                "master_tweet": {
                    "created_at": tweet['created_at'],
                    "text": tweet['full_text']
                },
                "author": {
                    "uid": tweet['user']['id_str'],
                    "image": tweet['user']['profile_image_url'],
                    "handle": tweet['user']['screen_name'],
                    "name": tweet['user']['name'],
                    "color": tweet['user']['profile_link_color']
                }
            }

            if current_user.is_authenticated:
                storm['unrolled_by_uid'] = current_user.id
                if current_user.userData['tw_handle'] == False:
                    storm['unrolled_by_handle'] = "anonymous"
                else:
                    storm['unrolled_by_handle'] = current_user.userData['tw_handle']
                is_anon = False
            else:
                is_anon = lmk
                storm['unrolled_by_handle'] = "anonymous"

            storm_id = db.reference('tweetstorms').push().key
            storm['story_id'] = storm_id
            db.reference('tweetstorms/' + storm_id).set(storm)
            task = u.getListOfIds.delay(id_str, tweet['user']['screen_name'], storm_id, is_anon)
            return {'status': 'queued', 'stormId': storm_id}
        except Exception as e:
            return {'status': 'failure', 'message': 'unable to parse tweet_url'}

annotation = reqparse.RequestParser()
annotation.add_argument('story_id', type=str, help='Unique ID for this story')
annotation.add_argument('tweet_id', type=str, help='Unique ID for this tweet')
annotation.add_argument('text', type=str, help='Text for this comment')

delete = reqparse.RequestParser()
delete.add_argument('story_id', type=str, help='Unique ID for this story')
delete.add_argument('tweet_id', type=str, help='Unique ID for this tweet')
delete.add_argument('annotation_id', type=str, help='Unique ID for this comment')

class Annotation(Resource):
    def post(self):
        data = annotation.parse_args(strict=True)
        tweetstorm = db.reference('tweetstorms/' + data['story_id']).get()
        if tweetstorm and data['tweet_id'] in tweetstorm['tweets'].keys():
            tweet = tweetstorm['tweets'][data['tweet_id']]
            ref = db.reference('tweetstorms/' + data['story_id']).child('tweets/' + data['tweet_id'])
            if tweet['hasAnnotations'] == False:
                ref.update({
                    'hasAnnotations': True,
                    'numberAnnotations': 1
                })
            else:
                ref.update({
                    'numberAnnotations': int(tweet['numberAnnotations'])+1
                })
            now = datetime.datetime.now()
            vis_timestamp = now.strftime("%a, %d %b at %I:%M %p")

            annotation_id = ref.child('annotations').push().key
            ref.child('annotations').child(annotation_id).set({
                "image": current_user.photoURL,
                "uid": current_user.id,
                "name": current_user.displayName,
                "text": data['text'],
                "unix_time": str(time.time()),
                "timestamp": vis_timestamp,
                "annotation_id": annotation_id
            })

            db.reference('tweetstorms/' + data['story_id']).update({
                'totalAnnotations': tweetstorm['totalAnnotations'] + 1
            })

            return {'status': 'success', 
                'image': current_user.photoURL,
                'name': current_user.displayName,
                'text': data['text'],
                'timestamp': vis_timestamp,
                'annotation_id': annotation_id,
                'tweet_id': data['tweet_id'],
                'story_id': data['story_id'],
                'message': 'comment posted'}
        else:
            return {'status': 'failure', 'message': 'no such story'}
    def delete(self):
        data = delete.parse_args(strict=True)
        tweetstorm = db.reference('tweetstorms/' + data['story_id']).get()
        if tweetstorm and data['tweet_id'] in tweetstorm['tweets'].keys():
            tweet = tweetstorm['tweets'][data['tweet_id']]
            ref = db.reference('tweetstorms/' + data['story_id']).child('tweets/' + data['tweet_id'])
            if len(tweet['annotations'].keys()) == 1:
                ref.update({
                    'hasAnnotations': False,
                    'numberAnnotations': int(tweet['numberAnnotations'])-1
                })
            else:
                ref.update({
                    'numberAnnotations': int(tweet['numberAnnotations'])-1
                })
            ref.child('annotations/' + data['annotation_id']).delete()

            db.reference('tweetstorms/' + data['story_id']).update({
                'totalAnnotations': tweetstorm['totalAnnotations'] - 1
            })

            return {'status': 'success', 'message': 'comment deleted'}
        else:
            return {'status': 'failure', 'message': 'no such story'}

collection = reqparse.RequestParser()
collection.add_argument('image', type=FileStorage, location='files')
collection.add_argument('title', type=str)
collection.add_argument('desc', type=str)
collection.add_argument('genre', type=str)

class NewCollection(Resource):
    def post(self):
        data = collection.parse_args()
        now = datetime.datetime.now()
        vis_timestamp = now.strftime("%a, %d %b at %I:%M %p")
        
        uuid = db.reference('collections').push().key

        current_dir = os.path.dirname(os.path.realpath(__file__))
        filename = current_dir + "/methods/tmp/collections/" + uuid + data['image'].filename
        data['image'].save(filename)
        data['image'].close()

        ul_task = u.uploadImg.delay(filename, uuid)
        ue_title = urllib.unquote(data['title'])
        ue_desc = urllib.unquote(data['desc'])
        ue_genre = urllib.unquote(data['genre'])

        payload = {
            "title": ue_title,
            "desc": ue_desc,
            "genre": ue_genre,
            "timestamp": vis_timestamp,
            "time": str(time.time()),
            "meta_url": "/static/img/processing.png",
            "image_url": "/static/img/processing.png",
            "author_uid": current_user.id,
            "collection_id": uuid,
            "author": {
                "name": current_user.displayName,
                "uid": current_user.id,
                "image": current_user.photoURL
            }

        }
        db.reference('collections').child(uuid).set(payload)
        return {'status': 'success', 'collection_id': uuid}

modify = reqparse.RequestParser()
modify.add_argument('action', type=str)
modify.add_argument('story_id', type=str)

class EditCollection(Resource):
    def put(self, uid):
        data = modify.parse_args()
        story = db.reference('tweetstorms/' + data['story_id']).get()
        collection = db.reference('collections/' + uid)
        if story and collection.get() and current_user.id == collection.get()['author_uid']:
            if data['action'] == "ADD":
                collection.child('stories/' + data['story_id']).set(story)
                return {'status': 'success'}
            elif data['action'] == "REMOVE":
                collection.child('stories').child(data['story_id']).delete()
                return {'status': 'success'}
        return {'status': 'failure', 'message': 'invalid inputs'}


class Feature(Resource):
    def get(self, uid):
        if current_user.id == config.adminId:
            collection = db.reference('collections/' + str(uid)).get()
            if collection:
                db.reference('featured').set(collection)
            else:
                return {'status': 'failure', 'message': 'no such collection'}
        else:
            return {'status': 'failure', 'message': 'unauthorized'}

crc_parser = reqparse.RequestParser()
crc_parser.add_argument('crc_token', type=str)

class TwitterWebhook(Resource):
    def get(self):
        args = crc_parser.parse_args()
        # creates HMAC SHA-256 hash from incomming token and your consumer secret
        sha256_hash_digest = hmac.new(config.twitter['consumerSecret'], msg=args['crc_token'], digestmod=hashlib.sha256).digest()

        # construct response data with base64 encoded hash
        response = {
            'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest)
        }

        # returns properly formatted json response
        return response
    def post(self):
        payload = json.loads(request.data)
        if "tweet_create_events" in payload.keys():
            if len(payload["tweet_create_events"][0]["in_reply_to_status_id_str"]) >= 6:
                trigger_text = payload["tweet_create_events"][0]["text"]
                trigger_id = payload["tweet_create_events"][0]["id"]

                hasKeyword = False

                for word in trigger_text.split(' '):
                    if word.lower() == "unroll":
                        hasKeyword = True

                if hasKeyword:
                    id_str = payload["tweet_create_events"][0]["in_reply_to_status_id"]
                    tweet = apiTwitter.GetStatus(status_id=id_str).AsDict()

                    now = datetime.datetime.now()
                    timestamp = now.isoformat()
                    vis_timestamp = now.strftime("%a, %d %b at %I:%M %p")

                    storm = {
                        "trigger_id": trigger_id,
                        "timestamp": timestamp,
                        "vis_timestamp": vis_timestamp,
                        "is_ready": False,
                        "totalAnnotations": 0,
                        "master_tweet": {
                            "created_at": tweet['created_at'],
                            "text": tweet['full_text']
                        },
                        "author": {
                            "uid": tweet['user']['id_str'],
                            "image": tweet['user']['profile_image_url'],
                            "handle": tweet['user']['screen_name'],
                            "name": tweet['user']['name'],
                            "color": tweet['user']['profile_link_color']
                        }
                    }

                    storm['unrolled_by_handle'] = payload["tweet_create_events"][0]["user"]["screen_name"]
                    storm_id = db.reference('tweetstorms').push().key
                    storm['story_id'] = storm_id
                    db.reference('tweetstorms/' + storm_id).set(storm)
                    task = u.getListOfIds.delay(id_str, tweet['user']['screen_name'], storm_id, False)
        return {"status": "success"}

class SetupTwitter(Resource):
    def get(self):
        url = "https://api.twitter.com/1.1/account_activity/all/staging/subscriptions.json"
        auth = OAuth1(config.twitter['consumerKey'], config.twitter['consumerSecret'], config.twitter['accessKey'], config.twitter['accessSecret'])
        r = requests.post(url, auth = auth)
        print r.request.headers
        return {'status': 'done', 'data': r.json()}
    def put(self):
        print "ok"
        # current wh 1040229066979401728
        url = 'https://api.twitter.com/1.1/account_activity/all/staging/webhooks.json?url=https%3A%2F%2Fadae1b9b.ngrok.io%2Fwebhook%2Ftwitter'
        auth = OAuth1(config.twitter['consumerKey'], config.twitter['consumerSecret'], config.twitter['accessKey'], config.twitter['accessSecret'])
        r = requests.post(url, auth=auth)
        return {'status': 'done', 'data': r.json()}
    def delete(self):
        url = "https://api.twitter.com/1.1/account_activity/all/staging/webhooks/1040229066979401728.json"
        auth = OAuth1(config.twitter['consumerKey'], config.twitter['consumerSecret'], config.twitter['accessKey'], config.twitter['accessSecret'])
        r = requests.delete(url, auth=auth)
        return {'status': 'done'}

endpoints.add_resource(Story, '/v1/story')
endpoints.add_resource(Annotation, '/v1/annotation')
endpoints.add_resource(NewCollection, '/v1/collection')
endpoints.add_resource(EditCollection, '/v1/collection/<uid>')
endpoints.add_resource(Feature, '/v1/feature/<uid>')
endpoints.add_resource(TwitterWebhook, '/webhook/twitter')

endpoints.add_resource(SetupTwitter, '/t1')
