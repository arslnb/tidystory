import os  
from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions
from app import apiTwitter as api
from cloudinary.uploader import upload
from app.configs import staging as config
from firebase_admin import db
from app import celery
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
from flask import render_template
from app import apiTwitter
from app import app
import cloudinary
import textwrap
import requests
import datetime
import random

now = datetime.datetime.now()

@celery.task
def getListOfIds(tweet_id, handle, stormId, is_anon):
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=opts)

    # Construct the URL
    twUrl = "https://twitter.com/%s/status/%s" % (handle, tweet_id)
    driver.get(twUrl)

    try:
        upper_replies = driver.find_element_by_css_selector(".permalink-in-reply-tos") 
        list_of_replies = driver.find_elements_by_css_selector(".permalink-in-reply-tos #stream-items-id .ThreadedConversation-tweet")
        firstTweet = list_of_replies[0].find_element_by_css_selector('.tweet')
        newTweetId = firstTweet.get_attribute('data-tweet-id')
        driver.quit()
        return getListOfIds(newTweetId, handle, stormId, is_anon)
    except NoSuchElementException:
        pass

    try:
        more_replies = driver.find_element_by_css_selector(".ThreadedConversation-moreReplies") 
        more_replies.find_element_by_css_selector('.ThreadedConversation-moreRepliesLink').click()
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.invisibility_of_element_located(more_replies))
    except NoSuchElementException:
        pass
  
    # GET THE main tweet
    storm = {}

    try:
        permalink_tweet = driver.find_element_by_css_selector('.permalink-tweet-container .permalink-tweet')
        storm[1] = {
            "id": permalink_tweet.get_attribute('data-tweet-id'),
            "text": permalink_tweet.find_element_by_css_selector('.tweet-text').text
        }
    except NoSuchElementException:
        print "RAISE THIS"


    # Check for lower replies
    try:
        lower_replies = driver.find_element_by_css_selector(".replies-to .ThreadedConversation--selfThread") 
        tweets = lower_replies.find_elements_by_css_selector('.ThreadedConversation-tweet')
        counter = 2
        for tweet in tweets:
            storm[counter] = {
                "id": tweet.find_element_by_css_selector('.tweet').get_attribute('data-tweet-id'),
                "text": tweet.find_element_by_css_selector('.tweet-text').text
            }
            counter += 1
    except NoSuchElementException:
        pass
    driver.quit()
    finalStorm = cleanThreadObject(storm, stormId, is_anon)
    return finalStorm

def cleanThreadObject(storm, stormId, is_anon):
    finalStorm = {}
    vis_timestamp = now.strftime("%a, %d %b at %I:%M %p")
    for index in storm.keys():
        tw = storm[index]
        tweet = getTweetBreakDown(tw)
        tweet_id = db.reference('tweetstorms/' + stormId).child("tweets").push().key
        tweet['ts_uid'] = tweet_id
        db.reference('tweetstorms/' + stormId).child("tweets").child(tweet_id).set(tweet)

    # Get the meta image
    s_ref = db.reference('tweetstorms/' + stormId).get()

    metaImg = {
        "name": s_ref['author']['name'],
        "handle": s_ref['author']['handle'],
        "tweet": storm[1]['text'],
        "unroller": s_ref['unrolled_by_handle'],
        "uid": stormId
    }

    metaUrl = generateImg(metaImg)

    db.reference('tweetstorms/' + stormId).update({
        'is_ready': True,
        'meta_url': metaUrl,
        'master_tweet': {
            'created_at': vis_timestamp,
            'text': storm[1]['text']
        }
    })

    if not is_anon:
        if s_ref['unrolled_by_handle'] != "anonymous":
            if s_ref['trigger_id'] != False:
                apiTwitter.CreateFavorite(status_id = int(s_ref['trigger_id']))
                apiTwitter.PostUpdate(TweetOut(s_ref['unrolled_by_handle'], stormId), in_reply_to_status_id = int(s_ref['trigger_id']))
            else:
                apiTwitter.PostUpdate(TweetOut(s_ref['unrolled_by_handle'], stormId))
    else:
        with app.app_context():
            rendered_html = render_template("email.html", action_url = stormId, meta_url = metaUrl)
        requests.post("https://api.mailgun.net/v3/mg.tidystory.com/messages",
        auth=("api", "f96c85e220d450284d311a3fd8700e1e-7bbbcb78-bd9072e1"),
        data={"from": "Team Tidystory <concierge@tidystory.com>",
              "to": [is_anon],
              "subject": "It's here!",
              "html": rendered_html})
    return finalStorm

def getTweetBreakDown(tweetInfo):
    tweetModel = api.GetStatus(status_id=tweetInfo['id']).AsDict()

    returnedTweet = {
        "hasMedia": False,
        "hasHashtags": False,
        "hasUrls": False,
        "hasAnnotations": False,
        "text": tweetModel['full_text'],
        "id": tweetModel['id_str']
    }

    if 'media' in tweetModel.keys():
        returnedTweet['hasMedia'] = True
        returnedTweet['media'] = {}
        for media in tweetModel['media']:
            sInd = returnedTweet['text'].find(media['url'])
            if sInd != -1:
                eInd = sInd + len(media['url'])
                returnedTweet['text'] = returnedTweet['text'][:sInd] + returnedTweet['text'][eInd:]
            if media['type'] == "animated_gif":
                returnedTweet['media'][str(media['id'])] = {
                    "type": "animated_gif",
                    "link": media['video_info']['variants'][0]['url'],
                    "image": media['media_url_https']
                }
            elif media['type'] == "video":
                returnedTweet['media'][str(media['id'])] = {
                    "type": "video",
                    "link": media['video_info']['variants'][0]['url'],
                    "image": media['media_url_https']
                }
            elif media['type'] == "photo":
                returnedTweet['media'][str(media['id'])] = {
                    "type": "photo",
                    "link": media['media_url_https']
                }
            else:
                pass
    
    if len(tweetModel['hashtags']) >= 1:
        hashtagCounter = 0
        returnedTweet['hashtags'] = {}
        returnedTweet['hasHashtags'] = True
        for hashtag in tweetModel['hashtags']:
            returnedTweet['hashtags'][hashtagCounter] = hashtag
            hashtagCounter += 1

    if len(tweetModel['urls']) >= 1:
        urlCounter = 0
        returnedTweet['urls'] = {}
        returnedTweet['hasUrls'] = True
        for url in tweetModel['urls']:
            reqUrl = "http://api.linkpreview.net/?key=%s&q=%s" % (config.lp['key'], url['expanded_url'])
            req = requests.get(reqUrl)
            linkInfo = req.json()
            returnedTweet['urls'][urlCounter] = linkInfo
            urlCounter += 1
    return returnedTweet

def generateImg(story):
    current_dir = os.path.dirname(os.path.realpath(__file__))

    base = Image.open(config.metaBase["img"])
    draw = ImageDraw.Draw(base)

    tx = 75
    t1_y = 75
    t2_y = 115
    t3_y = 190

    font0 = ImageFont.truetype(config.metaBase["font1"], 50)
    font1 = ImageFont.truetype(config.metaBase["font1"], 40)
    font2 = ImageFont.truetype(config.metaBase["font2"], 32)
    font3 = ImageFont.truetype(config.metaBase["font3"], 32)

    draw.text((tx, t1_y), story['name'], font=font1, fill=(216,216,216,255))
    draw.text((tx, t2_y), "@" + story['handle'], font=font2, fill=(216,216,216,130))
    draw.text((226, 498), "@" + story['unroller'], font=font3, fill=(216,216,216,255))

    lines = textwrap.wrap("\"" + story["tweet"][:163] + "...\"", width=48)
    for line in lines:
        draw.text((tx, t3_y), line, font=font0, fill=(216,216,216,255))
        t3_y += 70

    filename = current_dir + "/tmp/" + story["uid"] + ".png"
    base.save(filename, "PNG")

    cloudinary.config(
        cloud_name = 'tidystory',  
        api_key = '929736318553763',  
        api_secret = '2DU6OC9SvRTIsD242Lc0ihHKdbU'  
    )

    url = upload(filename)['secure_url']
    os.remove(filename)
    return url

def generateCollectionImg(collection):
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Base canvas
    base = Image.new('RGB', (1200, 598))

    # image of the collection
    collection_image = Image.open(collection['image'])
    collection_image = ImageOps.fit(collection_image, (1200, 598), Image.ANTIALIAS, 0, (0.5, 0.5))
    base.paste(collection_image, (0,0))

    draw = ImageDraw.Draw(base, 'RGBA')

    # Black transparent background
    draw.polygon([(0, 0), (1200, 0), (1200, 598), (0, 598)], (0, 0, 0, 125))
    draw.polygon([(76, 476), (904, 476)], (255, 255, 255, 65))
    del draw
    
    text_draw = ImageDraw.Draw(base)
    tag = Image.open(config.metaBase["collectionTag"])
    base.paste(tag, (76,190), mask=tag)

    tx = 76
    t3_y = 230

    font1 = ImageFont.truetype(config.metaBase["font3"], 28)
    font2 = ImageFont.truetype(config.metaBase["font3"], 90)

    message = "a tidystory collection on %s by %s" % (collection['genre'], collection['author_handle'])

    text_draw.text((tx, 60), "tidystory", font=font1, fill=(216,216,216,155))
    text_draw.text((850, 60), "https://tidystory.com", font=font1, fill=(216,216,216,155))
    text_draw.text((tx, 517), message, font=font1, fill=(216,216,216,155))

    if len(collection["title"]) > 46:
        title_text = collection["title"][:46] + "..."
    else:
        title_text = collection["title"]
    
    lines = textwrap.wrap(title_text, width=28)
    for line in lines:
        text_draw.text((tx, t3_y), line, font=font2, fill=(255,255,255,200))
        t3_y += 100

    output = current_dir + "/tmp/collections/collection_meta_" + collection["uid"] + ".png"
    base.save(output)

    cloudinary.config(
        cloud_name = 'tidystory',  
        api_key = '929736318553763',  
        api_secret = '2DU6OC9SvRTIsD242Lc0ihHKdbU'  
    )

    url = upload(output)['secure_url']
    os.remove(output)
    return url

@celery.task
def uploadImg(filename, uuid):
    cloudinary.config(
        cloud_name = 'tidystory',  
        api_key = '929736318553763',  
        api_secret = '2DU6OC9SvRTIsD242Lc0ihHKdbU'  
    )

    image_url = upload(filename)['secure_url']
    collection = db.reference('collections/' + str(uuid)).get()

    meta_info = {
        "image": filename,
        "title": collection['title'],
        "uid": str(uuid),
        "genre": collection['genre'],
        "author_handle": collection['author']['name']
    }

    meta_url = generateCollectionImg(meta_info)
    os.remove(filename)

    db.reference('collections/' + str(uuid)).update({
        'image_url': image_url,
        'meta_url': meta_url
    })

    return True

def TweetOut(authorHandle, ShortId):
    options = ["Hey! Here's that story by @{authorHandle} that you requested. Have a nice one 😉 \n\n https://tidystory.com/storm/{ShortId}",
        "Hi 👋, hope you're excited to check out the story (by @{authorHandle}) you requested. Here it is —\n\n https://tidystory.com/storm/{ShortId}",
        "Hello! The story by @{authorHandle} is ready for you to read. Check it out here —\n\n https://tidystory.com/storm/{ShortId}"]
    message = random.choice(options)
    return message