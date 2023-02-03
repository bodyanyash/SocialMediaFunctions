import logging
import time

from botocore.exceptions import ClientError
from google_images_search import GoogleImagesSearch
import requests
from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects
from moviepy.video.tools.subtitles import SubtitlesClip
from mutagen.mp3 import MP3
import numpy as np
from PIL import Image
import youtube_dl
import regex as re
import pyimgur
import mimetypes
import random

from scipy.ndimage import gaussian_filter

from srtUtils import *
from transcribeUtils import *
from videoUtils import *


def getYTVid(url, filename):
    ydl_opts = {'outtmpl': filename + ".mp4",
                'cachedir': False}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# gis = GoogleImagesSearch('AIzaSyAFmYctUnDNrRum4l7tiRQSIj4Hv3-MYAk', '1378e7cef54b81c1d')
def getgoogleimages(keywords, num=2):
    gis = GoogleImagesSearch('AIzaSyC4e5qJzWhGkrPVjC_6ne9n-GF4hkZMow4', 'b9b994f0192875328')

    for keyw in keywords:
        try:
            _search_params = {
                'q': keyw,
                'num': num,
                'safe': 'off',
                'fileType': 'jpg',
                'imgType': 'photo',
                'imgSize': 'LARGE'}

            gis.search(search_params=_search_params, path_to_dir='gImages')
        except:
            pass


def combineAudioVideo(video, audio, stretchvidtoaud='yes'):
    video = VideoFileClip(video)
    audio = AudioFileClip(audio)
    if stretchvidtoaud == 'yes':
        fxSpeed = video.duration / audio.duration
    else:
        fxSpeed = 1

    video = video.fx(vfx.speedx, factor=fxSpeed)
    video = video.set_audio(audio)
    video.write_videofile('temp.mp4')
    os.rename('temp.mp4', video.filename)
    return video.filename


def PexelsAssets(keyw, typer='photo', results=15):
    # print('Pexels assets: ', keyw)
    api_key = '563492ad6f917000010000018f2c5a972de44f8caa6fdb1c09c9525c'
    my_obj = {'query': keyw, 'per_page': results}
    assets = []
    if typer == 'video':
        # print('video')
        video_base_url = 'https://api.pexels.com/videos/search'
        x = requests.get(video_base_url, headers={'Authorization': api_key}, params=my_obj)
        print(x.text)
        videos = x.json()['videos']
        for variable in range(len(videos)):
            # print('variable: ', variable)
            for v2 in range(len(videos[variable]['video_files'])):
                # print('v2: ', v2)
                dl = 0
                if videos[variable]['video_files'][v2]['width'] == 1920:
                    dl = v2
                else:
                    pass

            new = videos[variable]['video_files'][dl]['link']

            typerp = re.search('[^/]*$', videos[variable]['video_files'][dl]['file_type'])[0]
            # print('new', new, '; ', 'typer', typer)

            namer = str(videos[variable]['id']) + '.' + typerp

            if (str(videos[variable]['id'])).upper() in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                                                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3',
                                                         'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']:
                print('innit')
                namer = 'a' + namer
            # print(namer)
            f = open(namer, 'wb')
            # print('writing')
            f.write(requests.get(new).content)
            # print('written')
            assets.append(namer)

    else:
        video_base_url = 'https://api.pexels.com/v1/search'
        x = requests.get(video_base_url, headers={'Authorization': api_key}, params=my_obj)
        photos = x.json()['photos']
        for variable in range(len(photos)):
            new = photos[variable]['src']['landscape']
            f = open(keyw + str(variable) + '.jpeg', 'wb')
            f.write(requests.get(new).content)
            assets.append(keyw + str(variable) + '.jpeg')

    return assets


def ImgurUpload(path):
    CLIENT_ID = "b66b3e6daf0b7d9"
    uploaded_image = ' '
    im = pyimgur.Imgur(CLIENT_ID)
    try:
        uploaded_image = im.upload_image(path)

    except:
        print('imgur upload failed')
    return uploaded_image.link


def AssetVerify(path, typer='photo'):
    print(typer)
    if typer == 'video':
        clip2 = VideoFileClip(path).resize(height=1080)
        clip2.save_frame("heyimtrying.png", clip2.duration / 2)
        path = "heyimtrying.png"

    url = "https://image-labeling1.p.rapidapi.com/img/label"
    purl = ImgurUpload(path)
    # print(purl)

    payload = "{\n    \"url\": \"" + purl + "\"\n}"
    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': "67839f8c78msh6e52610ebfa59e8p1ef5a6jsn75b1d38e7651",
        'x-rapidapi-host': "image-labeling1.p.rapidapi.com"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)


def blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian_filter(image.astype(float), sigma=2)


def Montage(assets=[], aud='test.mp3', name='temp.mp4'):
    print('Montaging')
    vids = []
    pics = []
    starts = []
    resizzler = []
    dur = 0
    trans = 1
    for clip in assets:
        mimestart = mimetypes.guess_type(clip)[0]
        if mimestart != None:
            mimestart = mimestart.split('/')[0]

            if mimestart == 'video':
                pip = VideoFileClip(clip)
                vids.append(pip)
            elif mimestart == 'image':
                pip = ImageClip(clip)
                pics.append(pip)
    random.shuffle(vids)
    random.shuffle(pics)

    for i in range(len(vids)):
        starts.append(dur)
        dur = dur + vids[i].duration - trans
        if 1920 / 1080 < vids[i].w / vids[i].h:
            vids[i] = vids[i].set_start(dur).crossfadein(trans).set_position('center').crossfadeout(trans).resize(
                1920 / vids[i].w)
        else:
            vids[i] = vids[i].set_start(dur).crossfadein(trans).set_position('center').crossfadeout(trans).resize(
                1080 / vids[i].h)

    lenner = dur + vids[-1].duration
    bg = VideoFileClip(assets[0]).fx(vfx.speedx, final_duration=lenner).fl_image(blur).resize((1920, 1080))
    finals = vids
    # vids[i].set_start(starts[i]).crossfadein(trans).set_position('center').crossfadeout(trans).resize(resizzler[i])
    # for i in range(len(vids))]

    finals.insert(0, bg)
    aud2 = AudioFileClip(aud)
    final = CompositeVideoClip(finals, (1920, 1080)).on_color(size=(1920, 1080), color=(47, 73, 255)).fx(vfx.speedx,
                                                                                                         final_duration=aud2.duration)

    final.audio = aud2
    if '/' in aud:
        aud = aud.split('/')[1]
    response = createTranscribeJob(region, inbucket, aud)
    while (response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
        print("."),
        time.sleep(30)
        response = getTranscriptionJobStatus(response["TranscriptionJob"]["TranscriptionJobName"])
    transcript = getTranscript(str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]))
    writeTranscriptToSRT(transcript, 'en', "subtitles-en.srt")
    createSubbedClip(final, "subtitles-en.srt", name, "audio-en.mp3", True)


    #final.write_videofile(name)

    print('vids: ', vids, ' pics: ', pics)
    return name

def upload_file(file_name, bucket, object_name=None):

    # If S3 object_name was not specified, use file_name
    if object_name is None and '/' not in file_name:
        object_name = file_name
    elif '/' in file_name:
        object_name = file_name.split('/')[1]
    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# assets, typer = PexelsAssets('happy', 'video', 15)
assets = ['blinds0.mp4', 'addition0.mp4', 'ceramic0.mp4', 'contractors0.mp4']
PexelsAssets('com', 'video', 2)

# , 'happy2.mp4', 'happy3.mp4', 'happy4.mp4', 'happy5.mp4', 'happy6.mp4', 'happy7.mp4', 'happy8.mp4', 'happy9.mp4', 'happy10.mp4', 'happy11.mp4', 'happy12.mp4', 'happy13.mp4', 'happy14.mp4']
#upload_file('RLX/RLXspeech.mp3', 'justin-speech-synthesis-bucket')
#Montage(assets, 'RLX/RLXspeech.mp3', 'pungy.mp4')




'''
assetss = [VideoFileClip(clip) for clip in assets]
starts = []
resizzler = []
dur = 0
trans = 1
for i in range(len(assetss)):
    starts.append(dur)
    dur = dur + assetss[i].duration - trans
    if 1920 / 1080 < assetss[i].w / assetss[i].h:
        resizzler.append(1920 / assetss[i].w)
    else:
        resizzler.append(1080 / assetss[i].h)

vidder = [assetss[i].set_start(starts[i]).crossfadein(trans).set_position('center').crossfadeout(trans).resize(resizzler[i]) for i in range(len(assetss))]
wipper = CompositeVideoClip(vidder, (1920, 1080))
wipper.write_videofile('pungy.mp4')
#for i in assets:
#   AssetVerify(i, typer)





print(PexelsAssets('dog', 'photo'))
getYTVid('https://www.youtube.com/watch?v=mCHRjTEfOBU', 'Vid')
file = combineAudioVideo("vid.mp4", "FUBO/FUBOgraphspeech.mp3")
print(file)

name = "small.mp4"
my_clip = VideoFileClip(name)
my_clip.write_videofile(name)

some_file_name = "some_file_name"
my_clip.write_videofile(some_file_name + ".mp4")

some_file_name = "another_name"
my_clip.write_videofile(some_file_name + ".mp4")





'''

# kek = ['stock markets']
# getgoogleimages(kek, 6)
