import mimetypes
from pydub import AudioSegment
import os
import csv
import json
import datetime
from tkinter.filedialog import askopenfilename
from moviepy.editor import *
import threading

# Function for converting audio to an mp3 format
def convertToMp3(file=''):
    if file == '':  # See if function is given a file to use
        return 'Supply an audio file'
    else:  # Assuming we have an audio file (not mp3), change it into an mp3 file
        AudioSegment.from_file(file).export(file.split('.')[0] + '.mp3', format="mp3")
        return file.split('.')[0] + '.mp3'


#Function to handle the export
def exportSnack(snack, newtitle, flag):
    if flag == 'audio':
        snack.write_audiofile(newtitle, codec='mp3', bitrate='96k')
    elif flag == 'video':
        snack.write_videofile(newtitle, bitrate="3000k", fps=30, codec='mpeg4')


# Function to extract audio between to times in seconds from a bigger audio clip
def cutOutSnack(start, end, ffile, newtitle = '', flag ='audio'):
    if type(newtitle) is None:
        newtitle = ''
    originalname = ffile.split('/')[-1].split('.')[
        0]  # this is the name of the file without the extension that we are using for source
    path = originalname + "Outputs/"
    fullpath = ffile.rsplit('/', 1)[0] + '/'
    suffix = ''     #File type to append to title

    #STOPPPPPPP
    #Check if video or audio and then define snack accordingly
    if flag == 'audio':
        max = AudioFileClip(ffile).duration
        if end > max:  # if end is past end of file, just make it end of file
            end = max
        startms = start * 1000  # Pydub works in ms so convert sec to millisec
        endms = end * 1000

        if start > end or start > max or end > max:
            raise Exception(
                "Your time bounds are off. Please check that times are within file length and start times are before end times. Maxclip duration: " + str(
                    max))
        snack = AudioFileClip(ffile)  # define the segment of audio
        suffix = '.mp3'


    elif flag == 'video':
        snack = VideoFileClip(ffile)
        max = snack.duration
        if end > max:  # if end is past end of file, just make it end of file
            end = max
        if start > end or start > max or end > max:
            raise Exception(
                "Your time bounds are off. Please check that times are within file length and start times are before end times. Maxclip duration: " + str(
                    max))
       #Scale/Crop video to snack size
        width = 700
        height = 900
        if width / height > snack.w / snack.h:
            snack = snack.subclip(start, end).set_position('center').resize(width / snack.w)
            snack = snack.fx(vfx.crop, x_center=snack.w / 2, y_center=snack.h / 2, width=width, height=height)
        else:
            snack = snack.subclip(start, end).set_position('center').resize(height / snack.h)
            snack = snack.fx(vfx.crop, x_center=snack.w / 2, y_center=snack.h / 2, width=width, height=height)

        suffix = '.mp4'

    if newtitle == '':  # Check if title was supplied. if not just use timestamps to name
        newtitle = originalname + str(start) + '-' + str(end) + suffix
    else:
        newtitle = newtitle + suffix

    exportSnack(snack, newtitle, flag)

    if not os.path.isdir(fullpath + path):  # Check if folder already made
        os.mkdir(fullpath + path)
    os.replace(fullpath + newtitle, fullpath + path + newtitle)

    return 1

# Function for converting H:M:S timestamp into seconds (makes it usable by cutOutAudio function)
def convertTimeToSec(timestamp):
    if timestamp.count(':') == 2:
        date_time = datetime.datetime.strptime(timestamp, "%H:%M:%S")
        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
        seconds = a_timedelta.total_seconds()
        return seconds
    elif timestamp.count(':') == 1:
        date_time = datetime.datetime.strptime(timestamp, "%M:%S")
        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
        seconds = a_timedelta.total_seconds()
        return seconds
    elif timestamp.count(':') == 0:
        seconds = float(timestamp)
        return seconds
    else:
        raise Exception("Please use H:M:S format for time")


#------------------------------------------------------------------------------------------------------------------
# Ask for the file name of the audio file we want to slice
filename = askopenfilename()
print(filename)

# Check to see if the file is an audio file
mimestart = mimetypes.guess_type(filename)
print(mimestart)
flag = ''  #use this just to remember what kind of file we have
if mimestart != None:
    mimestart = mimestart[0].split('/')[0]
    print(mimestart)
    if mimestart == 'audio' and filename.split('.')[1] != 'mp3':  # if it is an audio file and not already an mp3, convert it to mp3 for predictable use later and update the filename
        filename = convertToMp3(filename)
        flag = 'audio'
    elif mimestart == 'video':  # if it is a video file, We will treat it different
        flag = 'video'
    elif filename.split('.')[1] == 'mp3':  # if it is an mp3 just do nothing
        flag = 'audio'
    else:
        raise Exception("Please use audio or video file")  # if neither audio or video, have user try again lol
print(filename)

cutsfilename = askopenfilename()  # Get the filename containing the timestamps that we will use to create our cuts
print(cutsfilename)
# Check what the format of the cuts file is so we can handle appropriately


if cutsfilename.split('.')[1] == 'json':  # JSON Processing
    with open(cutsfilename) as json_file:
        data = json.load(json_file)
elif cutsfilename.split('.')[1] == 'csv':  # CSV Processing
    data = {'clips': []}  # trying to match the json format
    with open(cutsfilename, 'r') as datar:
        for line in csv.DictReader(datar):
            data['clips'].append(line)

# Iterate through the clips json structure and send it to extraction function
for clip in data['clips']:
    start = clip['start']
    if start == '':
        start = convertTimeToSec('0')
    else:
        start = convertTimeToSec(clip['start'])
    end = clip['end']
    if end == '':
        end = convertTimeToSec(str(int(start) + 7))
    else:
        end = convertTimeToSec(clip['end'])
    newtitle = clip['title']
    cutOutSnack(start, end, filename, newtitle, flag)

print(data)






