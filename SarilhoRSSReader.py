import feedparser
import os
import requests
import shutil
import tweepy
import pytumblr
import TwitterAPI
import facebook
import json
from mastodon import Mastodon


tumblr_consumer_key    = 'a'
tumblr_consumer_secret = 'b'
tumblr_token           = 'c'
tumblr_token_secret    = 'd'
tumblr_blogName = "p"

t_api_key             = "e"
t_api_key_secret      = "f"
t_bearer_token        = "g"
t_access_token        = "h"
t_access_token_secret = "i"

twitter_client_id = "j"
twitter_client_secret = "k"

fb_app_key    = "l"
fb_app_secret = "m"
fb_long_token = "n"

ig_user_id = "o"

mastodon_access_token = "q"
masto_instance = 'r'

#Tumblr
client  = pytumblr.TumblrRestClient(tumblr_consumer_key, tumblr_consumer_secret, tumblr_token, tumblr_token_secret)

#Twitter APIs, I used two for some reason
twitter = TwitterAPI.TwitterAPI(t_api_key, t_api_key_secret, t_access_token, t_access_token_secret)

twitter_auth = tweepy.OAuthHandler(t_api_key, t_api_key_secret)
twitter_auth.set_access_token(t_access_token, t_access_token_secret)

twitter_client = tweepy.Client( bearer_token        = t_bearer_token,
                                consumer_key        = t_api_key,
                                consumer_secret     = t_api_key_secret,
                                access_token        = t_access_token,
                                access_token_secret = t_access_token_secret )

#file location so i keep track of the latest RSS post i shared
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
rss_file = os.path.join(__location__, "rss_")

class RSSConsumer:

    def __init__(self):
        self.feedName = ""

    def run(self, feedName):
        try:
            # run rss
            self.feedName = feedName.split('/')[-1]
            print("-- Running RSS Feed Reader for Feed " + self.feedName + "--")

            blurb, comic_link, imageURL, description = FetchRss(feedName).getFeed()

            if blurb is not None and comic_link is not None and imageURL is not None:
                imageURL = imageURL.replace('<img src="', '').replace('" />', '')
                self.post_tumblr(  blurb, comic_link, imageURL, description)
                self.post_twitter( blurb, comic_link, imageURL, description)
                self.post_facebook(blurb, comic_link, imageURL, description)
                self.post_insta(   blurb, comic_link, imageURL, description)
                self.post_masto(   blurb, comic_link, imageURL, description)

        except Exception as e:
            print("Problem reading RSS feed... Reason: " + str(e))


    # description isn't used because instagram doesn't let you ALT images
    def post_insta(self, blurb, comic_link, imageURL, description):

        try:
            #I like making a different campaign link for comic updates
            comic_link = comic_link + "?utm_source=update_insta"

            if(self.feedName == "blurbfeed2"):
                blurb = "O Sarilho has updated! \n" + blurb + "\n #sarilho #spiderforest #WebComicUpdate \n" + comic_link
            else:
                blurb = blurb + "\n #sarilho #art #illustration"

            # Post the Media into a container first
            post_url = 'https://graph.facebook.com/v10.0/{}/media'.format(ig_user_id)
            payload = {
                'image_url': imageURL,
                'caption': blurb,
                'access_token': fb_long_token
            }
            r = requests.post(post_url, data=payload)

            print("Image uploaded. Result: " + r.text)
            result = json.loads(r.text)

            #use the ID of the uploaded media to publish to instagram
            if 'id' in result:
                creation_id = result['id']
                second_url = 'https://graph.facebook.com/v10.0/{}/media_publish'.format(ig_user_id)
                second_payload = {
                    'creation_id': creation_id,
                    'access_token': fb_long_token
                }
                r = requests.post(second_url, data=second_payload) #idk. maybe it wont result in 200 and I should've checked
                print('--------Just posted to Instagram--------')
            else:
                print('aaah oh nooo')
        except Exception as e:
            print("Problem updating Instagram... Reason: " + str(e))


    #No need for picture URL or description for Facebook but I'm keeping them here just in case I figure something later
    #The only reason i don't need imageURL is because at this point the image should be downloaded already
    def post_facebook(self, blurb, comic_link, imageURL, description):

        comic_link = comic_link + "?utm_source=update_facebook"

        if(self.feedName == "blurbfeed2"):
            f_blurb = blurb + " #spiderforest #webcomic #update | " + comic_link
        else:
            f_blurb = blurb + " #sarilho #art"

        try:
            graph = facebook.GraphAPI(fb_long_token)
            photo = open("imageURL", "rb") #read bytes good
            graph.put_photo(photo, message=f_blurb)
            photo.close()
            print('--------Just posted to Facebook--------')
        except Exception as e:
            print("Problem updating Facebook... Reason: " + str(e))


    def post_masto(self, blurb, comic_link, imageURL, description):

        try:
            mastodon     = Mastodon(access_token=mastodon_access_token, api_base_url=masto_instance)

            if (self.feedName == "blurbfeed2"):
                blurb = blurb + " #spiderforest #webcomic #update #MastoArt \n" + comic_link + "?utm_source=update_mastodon"
            else:
                blurb = blurb + " #sarilho #MastoArt"

            f = requests.get(imageURL)

            mime_type = "image/png"
            mtype = imageURL.split('.')[-1]

            if(not mtype):
                mtype = ""

            #too lazy to do a switch
            if(mtype == "gif"):
                mime_type = "image/gif"
            if(mtype == "jpg" or mtype == "jpeg"):
                mime_type = "image/jpeg"
            if(mtype == "png"):
                mime_type = "image/png"
            if (mtype == "bmp"):
                mime_type = "image/bmp"

            #post media first
            #description goes in media
            media = mastodon.media_post(f.content,
                                        mime_type=mime_type,
                                        description=description, focus=None,
                                        file_name=None, thumbnail=None,
                                        thumbnail_mime_type=None, synchronous=False)
            media_ids = [ media["id"] ]

            #post status linking to media
            #visibility is public because this is sporadic but if you're making a bot maybe set it to unlisted
            mastodon.status_post(blurb, in_reply_to_id=None, media_ids=media_ids, language="en", visibility="public")

            print('--------Just posted to Mastodon.Art--------')
        except Exception as e:
            print("Problem updating Mastodon... Reason: " + str(e))


    #maybe tumblr does let me put ALT text in pictures. but I don't know how to with this API.
    def post_tumblr(self, blurb, comic_link, imageURL, description):

        if(self.feedName == "blurbfeed2"):
            t_blurb = blurb + "<br/><p><a href='" + comic_link + "?utm_source=update_tumblr'>O SARILHO HAS UPDATED</a></p><br/>"
            t_blurb += "⭒ <a href='https://twitter.com/shizamura'>Twitter</a> " \
                   "⭒ <a href='https://instagram.com/shizamura'>Instagram</a> " \
                   "⭒ "
            tags=["o sarilho", "sarilho", "webcomic", "update", "spiderforest"]
        else:
            t_blurb = blurb + "<br/>⭒ <a href='" + comic_link + "?utm_source=tumblr'>Read O Sarilho</a> "
            t_blurb += "⭒ <a href='https://twitter.com/shizamura'>Twitter</a> " \
                   "⭒ <a href='https://instagram.com/shizamura'>Instagram</a> " \
                   "⭒ "
            tags=["o sarilho", "sarilho", "my art"]

        try:
            client.create_photo(
                            tumblr_blogName,
                            state="published",
                            tweet=t_blurb,
                            caption=t_blurb,
                            tags=tags,
                            source=imageURL)
            print('--------Just posted to Tumblr--------')
        except Exception as e:
            print("Problem updating Tumblr... Reason: " + str(e))

    def post_twitter(self, blurb, comic_link, imageURL, description):

        try:
            res = requests.get(imageURL, stream=True)

            if res.status_code == 200:
                with open("imageURL", 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                print('Image sucessfully Downloaded: to imageURL file')
            else:
                print('Image Couldn\'t be retrieved')

            # download image from imageURL, save to local file. Use read bytes for this.
            file = open('imageURL', 'rb')
            data = file.read()
            r = twitter.request('media/upload', None, {'media': data})

            print('TWITTER UPLOAD MEDIA SUCCESS' if r.status_code == 200 else 'TWITTER UPLOAD MEDIA FAILURE')

            if(self.feedName == "blurbfeed2"):
                tw_blurb = blurb + " " + comic_link + "?utm_source=update_twitter #sarilho #spiderforest"
            else:
                tw_blurb = blurb + " #sarilho #art"

            api = tweepy.API(twitter_auth, wait_on_rate_limit=True)

            # Upload image
            # Description goes on Media
            media = api.media_upload("imageURL")
            api.create_media_metadata(media.media_id, description)

            # Post tweet with media id reference
            twitter_client.create_tweet(text=tw_blurb, media_ids=[media.media_id])
            print('--------Just posted to Twitter--------')

        except Exception as e:
            print("Problem updating Twitter... Reason: " + str(e))

class FetchRss:
    def __init__(self, feedName):

        self.lastUpdate = 0
        self.RSSFileName = rss_file
        try:
            feedtitle = feedName.split('/')[-1]

            self.RSSFileName = rss_file + feedtitle + ".txt"

            file1 = open(self.RSSFileName, 'r', encoding="utf-8")
            self.lastUpdate = file1.readlines()[0]
        except Exception as e:
            print("Error reading rss.txt file. Reason: " + str(e))

        self.serverFeed = feedparser.parse(feedName)

    def getFeed(self):
        # Get difference between the threads fetched now and previously to tell what is new


        # gets ONLY the latest entry and records it to file so we don't post it twice
        if len(self.serverFeed.entries) > 0 :
            item       = self.serverFeed.entries[0]
            id         = item.guid

            if id != self.lastUpdate:
                with open(self.RSSFileName, 'w') as file1:
                    file1.write(str(id))

                # I write both text for post and alt text in the title because i can
                # separator |#|
                blurb      = str(item.title).split('|#|')[0]
                comic_link = item.link

                imgdescription = str(item.title).split('|#|')[-1]

                if(imgdescription == None):
                    imgdescription = ""

                imageURL       = str(item.description)

                return (blurb, comic_link, imageURL, imgdescription)

        return (None, None, None, None)


# running for the two different feeds
# you'll notice each of the methods makes the post slightly different depending on which feed it's getting the info from
# this is because I have both random art and comic updates going on. Each of them goes on a different feed.
# Feel free to check these out for the structure :)
rssCon = RSSConsumer()
rssCon.run("https://sarilho.net/feed/blurbfeed2") # comics
rssCon.run("https://sarilho.net/feed/socialfeed") # art








