import logging
import mimetypes

import requests
import os
import boto3
import regex as re
import webbrowser

from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
import copy
import json
from datetime import datetime, timedelta
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation, writers
from scipy.ndimage import gaussian_filter
from sigfig import round
from matplotlib.dates import DateFormatter
import language_check
import pandas as pd
import random
import shutil
from rake_nltk import Rake
import youtube_dl
import pyimgur
from google_images_search import GoogleImagesSearch
from moviepy.editor import *
from VidMaker.transcribeUtils import *
from VidMaker.srtUtils import *
import time
from VidMaker.videoUtils import *
from VidMaker.audioUtils import *


# function to download youtube video from a url and output to file
def getYTVid(url, filename):
    ydl_opts = {'outtmpl': filename + ".mp4",
                'cachedir': False}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# gis = GoogleImagesSearch('AIzaSyAFmYctUnDNrRum4l7tiRQSIj4Hv3-MYAk', '1378e7cef54b81c1d')
def getgoogleimages(keywords, num=2):
    gis = GoogleImagesSearch('AIzaSyC4e5qJzWhGkrPVjC_6ne9n-GF4hkZMow4', 'b9b994f0192875328')

    for keyw in keywords:
        print(keyw, num)
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




# uploads to imgur through our api key. returns url of image
def ImgurUpload(path):
    CLIENT_ID = "b66b3e6daf0b7d9"
    uploaded_image = ' '
    im = pyimgur.Imgur(CLIENT_ID)
    try:
        uploaded_image = im.upload_image(path)

    except:
        print('imgur upload failed')
    return uploaded_image.link


# checks contents of an image and gives us labels of what is in the image
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


# recursive function that gives the lowest 3 dictionary entries at the end of each branch of a dictionary. special splits of *; and ~ are used
def lowestdict(BigDict, PDict={}, Pkey=''):
    keyVals = ''
    curVal = ''
    for key in BigDict.keys():
        if isinstance(BigDict[key], dict):
            # print(key, 'is dict')
            curVal = curVal + '*;' + lowestdict(BigDict[key], BigDict, key)
            # print('curVal: ', curVal)
        else:
            # print(key, 'is not')
            keyVals = keyVals + '*;' + str(Pkey) + '~' + str(key) + '~' + str(BigDict[key])
            # print('KeyVal: ', keyVals)
    return keyVals + curVal


# function to split a CamelCase Sentence at the capital letters
def CamelCaseSplit(split=''):
    split = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', split))
    split = split.replace('  ', ' ')
    return split


# Further organizes stat details. function relies on lowestdict.
def get_stat_details(data):
    lowest3f = []
    lowest3 = []
    for i in lowestdict(data).split('*;'):
        if i != '' and i != "'":
            lowest3.append(i.split('~'))

    [lowest3f.append(x) for x in lowest3 if x not in lowest3f]
    return lowest3f


# function specifically for cleaning stats to be used for stock info. removes redundancies and useless fields
def stat_cleanup(stats):
    clean = []
    for i in stats:
        # print(i)
        if ('margin' in i[0].lower() or 'percent' in i[0].lower() or 'range' in i[0].lower() or 'change' in i[0].lower()
            or 'average' in i[0].lower() or 'yield' in i[0].lower() or 'growth' in i[0].lower() or 'ratio' in i[
                0].lower()) \
                and i[1] == 'raw':
            # print(i)
            clean.append(i)
        elif 'fmt' in i[1].lower() and \
                (re.search('[a-zA-Z]', i[2]) is not None and re.search('PM|AM', i[2]) is None):
            # print(i, "removed")
            clean.append(i)
        elif i[2] == 'None':
            clean.append(i)
        elif i[2].endswith('.00') and 'marketcap' in i[0].lower():
            clean.append(i)
    for i in clean:
        stats.remove(i)
    clean = []
    for i in stats:
        for j in stats:
            if i[0] == j[0] and (i[1] == 'raw' or i[1] == 'fmt' or i[1] == 'longFmt') and i[1] != j[1] \
                    and i not in clean and j not in clean:
                # print(i, 'dupe')
                clean.append(i)
    for i in clean:
        stats.remove(i)
    return stats


# function to get the content response from a url
def get_content_soup(url='https://finance.yahoo.com/gainers/'):
    rr = ''
    try:
        r = requests.get(url)
        rr = r.content
    except:
        print('Error getting content')
    return rr


# function that parses out stock info from the yahoo finance gainers/losers pages specifially
def get_stock_info_soup(text=''):
    try:
        allStocks = []
        stock = {}
        soup = BeautifulSoup(text, 'html.parser')
        length = len(soup.thead.tr.find_all('th'))
        depth = len(soup.tbody.find_all('tr'))

        # '''

        for j in range(0, depth):
            for i in range(0, length):
                try:
                    column = soup.thead.tr.find_all('th')[i]
                    head = column.text
                    row = soup.tbody.find_all('tr')[j]
                    data = row.find_all('td')[i]
                    stock[head] = data.text
                    # print(i)
                except:
                    print('Error creating individual stock')
            # print(j)
            # print(Stock)
            allStocks.append(copy.deepcopy(stock))
            # print(allStocks)

    except:
        print('error parsing soup')
        allStocks = {}
    return allStocks


# set the api headers to use for making yahoo finance calls
# function should be expanded to automatically switch to a second set when first set is out of free api calls
def get_api_headers():
    headers = {
        'x-rapidapi-key': "344f901a93mshba8e416a1781f4ep1cb25djsn761f18df3122",
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }
    return headers


# get stock summary from yahoo finance api
def get_stock_summary(headers, symb):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-summary"
    querystring = {"symbol": symb, "region": "US"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text


# get yahoo finance users comments on a stock
def get_stock_comments(headers, symb):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/conversations/list"
    querystring = {"symbol": symb, "messageBoardId": "finmb_24937", "region": "US", "userActivity": "true",
                   "sortBy": "createdAt", "off": "0"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    return response.text


# get general stock news for the day
def get_stock_news(headers):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/get-details"
    querystring = {"uuid": "9803606d-a324-3864-83a8-2bd621e6ccbd", "region": "US"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text


# get all the stock statistics for a certain symbol
def get_stock_statistics(headers, symb):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-statistics"
    querystring = {"symbol": symb, "region": "US"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text


# get the chart data for a stock for a certain range and interval
def get_stock_info_api(headers, symb, ranger='1d', interval='5m'):
    print('Getting Info', symb)
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-chart"
    querystring = {"interval": interval, "symbol": symb, "range": ranger, "region": "US"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    # print(response.text)
    return response.text


# function used to determine graph scale from the makegraph functions
def graphformat(dates):
    if dates <= timedelta(days=1):
        formatter = DateFormatter('%H:%M')
        # print('Format 1', formatter)
    elif dates <= timedelta(days=5):
        formatter = DateFormatter('%m-%d')
        # print('Format 5', formatter)
    elif dates <= timedelta(days=90):
        formatter = DateFormatter('%m-%d')
        # print('Format 90', formatter)
    else:
        formatter = DateFormatter('%Y-%m')
        # print('Format greater', formatter)

    return formatter


# function used to determine graph bounds from the makegraph functions
def graphbounds(x, y, previousClose):
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    if previousClose > ymax:
        ymax = previousClose
    elif previousClose < ymin:
        ymin = previousClose
    ymarg = (ymax - ymin) * 0.05
    ymin = ymin - ymarg
    ymax = ymax + ymarg
    return xmin, xmax, ymin, ymax


# function that creates a movie of the graph of the stock data plotted over time
def makegraph(jsons, quote='close'):
    print('Making Graph')

    plt.rcParams['animation.ffmpeg_path'] = r"C:\Users\ButterBoy\FFmpeg\bin\ffmpeg.exe"
    font = {'family': 'sans-serif',
            'weight': 'bold',
            'size': 15}
    plt.rc('font', **font)
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False

    data = json.loads(jsons)
    data1 = data["chart"]["result"][0]
    data2 = data1["indicators"]["quote"][0]

    # '''
    xi = data1["timestamp"]
    for i in range(0, len(xi)):
        xi[i] = datetime.fromtimestamp(xi[i])

    yi = data2[quote]
    x = []
    y = []
    for i in range(len(yi)):
        if yi[i] is not None:
            x.append(xi[i])
            y.append(yi[i])
    DateRange = max(x) - min(x)
    formatter = graphformat(DateRange)
    frames = len(x) - 1
    # print(yi, ' yi')
    lines = [None] * frames
    date = data1["meta"]["regularMarketTime"]
    symb = data1["meta"]["symbol"]

    date = datetime.fromtimestamp(date)
    if DateRange <= timedelta(days=1):
        date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
        previousClose = data1["meta"]["previousClose"]
    else:
        date = str(min(x).year) + '-' + str(min(x).month) + '-' + str(min(x).day) + ' to ' + str(
            max(x).year) + '-' + str(max(x).month) + '-' + str(max(x).day)
        previousClose = data1["meta"]["chartPreviousClose"]

    fig = plt.figure(figsize=[16, 9], dpi=100)
    xmin, xmax, ymin, ymax = graphbounds(x, y, previousClose)
    ax = plt.axes(xlim=(xmin, xmax), ylim=(ymin, ymax),
                  xlabel='Time', ylabel='Close Price', title=symb + ' ' + date)
    ax.xaxis.set_major_formatter(formatter)
    close = plt.hlines(previousClose, min(x), max(x), colors='k', linestyles='dashed',
                       label='Previous Close', data=None)
    plt.legend(handles=[close])
    ann = plt.annotate('', (x[0], y[0]))
    annP = plt.annotate('', (x[0], y[0]))

    for i in range(frames):
        lines[i] = (ax.plot([], [], lw=2, color='g'))[0]

    def init():
        for i in range(frames):
            lines[i].set_data([], [])
        return lines

    def animate(i):
        # print(i)
        tseg = [x[i], x[i + 1]]
        pseg = [y[i], y[i + 1]]

        ann.set_text('Change from previous chart close (' + str(previousClose) + '): ' + str(
            round(100 * (y[i + 1] - previousClose) / previousClose, sigfigs=2)) + '%')
        ann.set_position((x[0], (ymax - ymin) * 1.05 + ymin))
        annP.set_text('$' + str(round(y[i + 1], decimals=2)))
        annP.set_position((x[i + 1], y[i + 1]))
        lines[i].set_data(tseg, pseg)
        if pseg[1] >= pseg[0]:
            lines[i].set_color('g')
        else:
            lines[i].set_color('r')

        if pseg[1] > previousClose:
            ann.set_color('g')
        else:
            ann.set_color('r')
        # print(times)
        return lines

    anim = FuncAnimation(fig, animate, init_func=init, frames=frames, interval=200, blit=True)

    Writer = writers['ffmpeg']
    writer = Writer(fps=8, metadata=dict(artist='Me'), bitrate=1800)
    filename = symb + date + '.mp4'
    anim.save(symb + date + '.mp4', writer)

    speechfile = prepare_graph_speech(x, y, symb)

    return filename, speechfile


# adds a random interjection from the interjection text files
def addinterject(data):
    data = str(data)
    if '-' not in data:
        with open(random.choice(['Positives.txt', 'Neutral.txt']), encoding='UTF-8') as f:
            text = f.read()

        text = text.split(',')
    else:
        with open(random.choice(['Negatives.txt', 'Neutral.txt']), encoding='UTF-8') as f:
            text = f.read()

        text = text.split(',')

    text.append('')
    sent = random.choice(text) + '. '
    return sent


# Creates some basic phrases about the graph from the graph data
def prepare_graph_speech(x, y, symbol=''):
    speech = ''

    sections = 7
    x = np.array(x)
    y = np.array(y)
    d = {'Time': x, 'Price': y}
    Price = 'Price'
    Time = 'Time'

    df = pd.DataFrame(data=d)
    window = int(round(2))
    # print(window)

    if len(x) < 3:
        speech = "There really isn't too much data too look at here, but "

    highid = df[[Price]].idxmax()
    lowid = df[[Price]].idxmin()
    avg = y.sum() / len(y)
    df['Log_Ret'] = np.log(df[Price] / df[Price].shift(1))
    highlog = df[['Log_Ret']].idxmax()
    lowlog = df[['Log_Ret']].idxmin()
    df['Volatility'] = df['Log_Ret'].rolling(window).std() * np.sqrt(window)

    speech = speech + "Let's take a look at the graph and see what we can learn. "
    speech = speech + 'The high was ' + "{:.2f}".format(df.loc[highid[0]][Price]) + ' which happened at ' + str(
        df.loc[highid[0]][Time]) + '. '
    speech = speech + 'The low was ' + "{:.2f}".format(df.loc[lowid[0]][Price]) + ' which happened at ' + str(
        df.loc[lowid[0]][Time]) + '. '
    speech = speech + 'The average price for the time plotted is ' + "{:.2f}".format(avg) + '. '
    speech = speech + 'The total % change is ' + "{:.2f}".format(100 * (y[-1] - y[0]) / y[0]) + '%. ' + addinterject(
        100 * (y[-1] - y[0]) / y[0])
    speech = speech + 'The absolute change is ' + "{:.2f}".format((y[-1] - y[0])) + '. ' + addinterject(y[-1] - y[0])
    try:
        try:
            speech = speech + 'The best single opportunity for return was a logarithmic return rate of ' \
                     + "{:.2f}".format(df.loc[highlog[0]]['Log_Ret'] * 100) + '% which happened between ' + str(
                df.loc[highlog[0]][Time]) \
                     + ' and ' + str(df.loc[highlog[0] + 1][Time]) + '. ' + addinterject(
                df.loc[highlog[0]]['Log_Ret'] * 100)

        except (KeyError):
            try:
                speech = speech + 'The best single opportunity for return was a logarithmic return rate of ' \
                         + "{:.2f}".format(df.loc[highlog[0]]['Log_Ret'] * 100) + '% which happened between ' + str(
                    df.loc[highlog[0]][Time]) \
                         + ' and ' + str(df.loc[highlog[0] - 1][Time]) + '. ' + addinterject(
                    df.loc[highlog[0]]['Log_Ret'] * 100)
            except (KeyError):
                speech = speech + 'The best single opportunity for return was a logarithmic return rate of ' \
                         + "{:.2f}".format(df.loc[highlog[0]]['Log_Ret'] * 100) + '. '
        try:
            speech = speech + 'The worst single opportunity for return was a logarithmic return rate of ' \
                     + "{:.2f}".format(df.loc[lowlog[0]]['Log_Ret'] * 100) + '% which happened between ' + str(
                df.loc[lowlog[0]][Time]) \
                     + ' and ' + str(df.loc[lowlog[0] + 1][Time]) + '. ' + addinterject(
                df.loc[lowlog[0]]['Log_Ret'] * 100)
        except (KeyError):
            try:
                speech = speech + 'The worst single opportunity for return was a logarithmic return rate of ' \
                         + "{:.2f}".format(df.loc[lowlog[0]]['Log_Ret'] * 100) + '% which happened between ' + str(
                    df.loc[lowlog[0]][Time]) \
                         + ' and ' + str(df.loc[lowlog[0] - 1][Time]) + '. ' + addinterject(
                    df.loc[lowlog[0]]['Log_Ret'] * 100)
            except (KeyError):
                speech = speech + 'The worst single opportunity for return was a logarithmic return rate of ' \
                         + "{:.2f}".format(df.loc[lowlog[0]]['Log_Ret'] * 100) + '. '
    except (KeyError):
        speech = speech + 'The logarithmic return rate could not be calculated for the time plotted. '
    # print(df.loc[highid[0]][Price])
    # print(df.at[1, Price])
    # print(speech)
    # print(df)
    # print('here')
    return create_speech(speech, symbol + 'graphspeech.mp3')


# basically converts the long summary into a justing speech and throws some stats on at the end
def prepare_speech(jsons='', Soup='', LongSummary=''):
    speech = ''
    print('the long summary for the current stock: ', LongSummary)

    info = json.loads(jsons)
    name = info['price']['longName']
    intro = 'Here are some important statistics for ' + name + '. Their symbol is ' + Soup['Symbol'] + '.'

    speech = intro
    speech = speech + ' ' + LongSummary

    details = get_stat_details(info)
    details = stat_cleanup(details)
    # print(details)
    print('details for the speech: ', details)
    # These are the fields we are choosing from for yahoo api data
    with open("Fields.txt", encoding='UTF-8') as f:
        text = f.read()

    text = text.split(',')

    print('making sentences')
    for i in details:
        if i[0] in text:
            sentence = (make_sentence(i))
            if len(speech) + len(sentence) + 1 < 3000:
                speech = speech + ' ' + sentence
            if random.choice([0, 1]):
                speech = speech + ' ' + addinterject(i[2])
            print(i)

    # These are the fields we are choosing from for Soup data

    # Make function to 'randomize' choices

    print('the whole speech: ', speech)

    return create_speech(speech, Soup['Symbol'] + 'speech.mp3')


# function that takes in the cleaned stats and makes a sentence
def make_sentence(details):
    sentence = ''
    if details[1] == 'raw' or details[1] == 'fmt' or details[1] == 'longFmt':
        sentence = 'The ' + CamelCaseSplit(details[0]) + ' is ' + CamelCaseSplit(details[2]) + '.'
    else:
        sentence = 'The ' + CamelCaseSplit(details[1]) + ' is ' + CamelCaseSplit(details[2]) + '.'
    tool = language_check.LanguageTool('en-US')
    sentence = tool.correct(sentence)
    return sentence.replace('.00', '')


# gets the right data interval based on the data range for yahoo finance api
def getInterval(range):
    if range == '1d':
        inter = '5m'
    elif range == '5d':
        inter = '15m'
    elif range == '1mo':
        inter = '60m'
    elif range == '3mo':
        inter = '1d'
    elif range == '6mo':
        inter = '1d'
    elif range == '1y':
        inter = '1d'
    elif range == '2y':
        inter = '1d'
    elif range == '5y':
        inter = '1d'
    elif range == '10y':
        inter = '1d'
    elif range == 'ytd':
        inter = '1d'
    elif range == 'max':
        inter = '1d'
    # print(range, inter)
    return inter


# uploads a file to an s3 bucket
def upload_file(file_name, bucket='justin-blog-synthesis-bucket', object_name=None):
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


# uses amazon polly to create a speech
def create_speech(text, file_name='speech.mp3', vid='Justin', outbucket='justin-blog-synthesis-bucket'):
    polly = boto3.client('polly');

    if len(text) < 3000:
        print('Text under 3000')
        response = polly.synthesize_speech(Engine='neural', OutputFormat='mp3', Text=text, VoiceId=vid);

        body = response['AudioStream'].read()

        with open(file_name, 'wb') as file:
            file.write(body);
            file.close();
    else:
        response = polly.start_speech_synthesis_task(OutputS3BucketName=outbucket,
                                                     Engine='neural',
                                                     OutputFormat='mp3', Text=text, VoiceId=vid);
        print(response)
        while (response["SynthesisTask"]["TaskStatus"] == "scheduled" or response["SynthesisTask"][
            "TaskStatus"] == "inProgress"):
            print("...synthesis in progress..."),
            time.sleep(30)
            response = polly.get_speech_synthesis_task(TaskId=response["SynthesisTask"]["TaskId"])

        result = requests.get(str(response["SynthesisTask"]["OutputUri"]))
        s3 = boto3.client('s3')
        with open(file_name, 'wb') as f:
            s3.download_fileobj(outbucket, response["SynthesisTask"]["TaskId"] + '.mp3', f)

    return file_name


# basically useless now. plays or doesnt play a speech file after calling create_speech()
def use_polly(text='', play='no', vid='Justin'):
    if text == '':
        Inputs = input();
    else:
        Inputs = text

    create_speech(Inputs, vid);

    if play != 'no':
        webbrowser.open('speech.mp3')


# uses rake library to get keywords from a text input
def getkeywords(mytext):
    r = Rake()
    r.extract_keywords_from_text(mytext)
    keywords = r.get_ranked_phrases()
    tool = language_check.LanguageTool('en-US')
    # for i in range(len(keywords)):
    #   keywords[i] = tool.correct(keywords[i])
    return keywords


# get stock assets from pexels by type based on keywords.
def PexelsAssets(keyw, typer='photo', results=1):
    # print('Pexels assets: ', keyw)
    api_key = '563492ad6f917000010000018f2c5a972de44f8caa6fdb1c09c9525c'
    my_obj = {'query': keyw, 'per_page': results}
    assets = []
    if typer == 'video':
        print('getting pexel video')
        video_base_url = 'https://api.pexels.com/videos/search'
        x = requests.get(video_base_url, headers={'Authorization': api_key}, params=my_obj)
        # print(x.text)
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


# function needed to blur the background for the montages
def blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian_filter(image.astype(float), sigma=2)


# Compiles an array of assets into a sequential montage and replaces the audio with your new audio.
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

        if 1920 / 1080 < vids[i].w / vids[i].h:
            vids[i] = vids[i].set_start(dur).crossfadein(trans).set_position('center').crossfadeout(trans).resize(
                1920 / vids[i].w)
        else:
            vids[i] = vids[i].set_start(dur).crossfadein(trans).set_position('center').crossfadeout(trans).resize(
                1080 / vids[i].h)
        dur = dur + vids[i].duration - trans

    lenner = dur
    # + vids[-1].duration
    bg = VideoFileClip(assets[0]).fx(vfx.speedx, final_duration=lenner).fl_image(blur).resize((1920, 1080))
    finals = vids
    # vids[i].set_start(starts[i]).crossfadein(trans).set_position('center').crossfadeout(trans).resize(resizzler[i])
    # for i in range(len(vids))]

    finals.insert(0, bg)
    aud2 = AudioFileClip(aud)
    final3 = CompositeVideoClip(finals, (1920, 1080)).on_color(size=(1920, 1080), color=(47, 73, 255)).fx(vfx.speedx,
                                                                                                          final_duration=aud2.duration)

    final3.audio = aud2
    # final = concatenate_videoclips([final3, graphvid.resize((1920, 1080))])
    # final.write_videofile(name)

    print('vids: ', vids, ' pics: ', pics)
    return final3


# function that will overlay a video with new audio. If stretch is yes, the video will change speed to match audio length
def combineAudioVideo(video, audio, stretchvidtoaud='yes'):
    print('video: ', video, ' Audio: ', audio)
    video = VideoFileClip(video)
    audio = AudioFileClip(audio)
    if stretchvidtoaud == 'yes':
        fxSpeed = video.duration / audio.duration
    else:
        fxSpeed = 1

    video = video.fx(vfx.speedx, factor=fxSpeed)
    video = video.set_audio(audio)
    # video.write_videofile('temp.mp4')

    # os.remove(video.filename)
    # os.rename('temp.mp4', video.filename)
    return video
