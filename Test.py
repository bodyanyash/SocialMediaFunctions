import random

import language_check
from PIL import Image, ImageDraw, ImageFont
import sys
import textwrap
import markovify
from googleapiclient.errors import HttpError
from rake_nltk import Rake

import Google
import videoDetails
from Google2 import get_authenticated_service, initialize_upload


def getkeywords(text):
    r = Rake()
    r.extract_keywords_from_text(mytext)
    keywords = r.get_ranked_phrases()
    tool = language_check.LanguageTool('en-US')
    # for i in range(len(keywords)):
    #   keywords[i] = tool.correct(keywords[i])
    return keywords


mytext = open("Post", "r")
mytext = mytext.read()
with open('Post') as f:
    Title = f.readline()

keywords = getkeywords(mytext)
source_list = keywords
N = 30
keywords = source_list[:N]

def make_tags(keywords):
    tags = ''
    for word in keywords:
        tags = word + ', ' + tags
    return tags

tags = make_tags(keywords)
print(tags)


args = videoDetails.Video()
youtube = get_authenticated_service()
args.keywords = ''
args.title = Title
args.description = mytext + ' : Trawvidsec.net'
args.category = '28'
args.file = 'post-final.mp4'
try:
    initialize_upload(youtube, args)
except HttpError as e:
    print('An HTTP error %d occurred:\n%s') % (e.resp.status, e.content)

#Google.upload_video('post-final.mp4', 'pil_text_font.png', "CMMC Compliance: Federally Mandated Cybersecurity", mytext + ' : Trawvidsec.net', tags=tags)
