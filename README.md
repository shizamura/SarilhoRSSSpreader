# SarilhoRSSSpreader
I spread comic updates and art to my socials 🔥

Socials:
* Tumblr
* Mastodon
* Facebook
* Instagram
* Twitter

Maybe one day if I manage:
* Ko-fi
* Deviantart

# Notes

Script reads information from an RSS feed. This provides a URL for an image, text for sharing and image description. Updates only for the first entry of the feed, stores information about the last entry read to avoid duplicate posts. 

The RSS feed is generated via Wordpress template. Check https://sarilho.net/feed/socialfeed for the structure I'm using.

You'll need access tokens for pretty much everything here. I got them by creating apps in each site and giving them permission to manage my accounts. The same app can be used for both instagram and facebook (make sure you have instagram permissions enabled, and your facebook page and instagram profile are connected).

# Read my Comic: https://sarilho.net/

# Requirements
- python-facebook-api 0.15.0
- Mastodon.py 1.8.0
- PyTumblr 0.1.0
- Feedparser 6.0.10
- Requests 2.28.1
- Tweepy 4.12.1
- TwitterAPI 2.8.1
