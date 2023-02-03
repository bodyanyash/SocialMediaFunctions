import Thumbnail
from MyFunctions import *

#Settings For AWS
global region, inbucket, outbucket
region = 'us-east-1'
outbucket = inbucket = 'justin-blog-synthesis-bucket'
outfiletype = 'mp3'
outlang = 'en-US'

mytext = open("Post", "r")    #Make first line of file the Title
mytext = mytext.read()
with open('Post') as f:
    Title = f.readline()

keywords = getkeywords(mytext)  # Uses my function to scrape contextually for keywords
speech = create_speech(mytext)  # Send text to polly and donload mp3 file when synthesis is complete
source_list = keywords
N = 30                          # Number of Pexel Assets to retrieve
keywords = source_list[:N]      # Get 30 first keywords
print(keywords)
assets = []
print('getting assets')
for keyw in keywords:
    # assets = assets + PexelsAssets(keyw, 'photo', 0)
    assets = assets + PexelsAssets(keyw, 'video', 1)    # get stock assets from pexels and add file name to to assets array
assets = list(set(assets))
half1 = Montage(assets, speech, 'montage.mp4')          # returns CompositeVideoClip of the assets with the speech and names it montage.mp4)

upload_file(speech, inbucket)                           #Put speech in AWS bucket
response = createTranscribeJob(region, inbucket, speech)    #Create a transcribe job in AWS and await the response
while (response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
    print("."),
    time.sleep(30)
    response = getTranscriptionJobStatus(response["TranscriptionJob"]["TranscriptionJobName"])
transcript = getTranscript(str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]))
writeTranscriptToSRT(transcript, 'en', "subtitles-en.srt")
createSubbedClip(half1, "subtitles-en.srt", 'post-final.mp4', "audio-en.mp3", True) #Create clip that has the subtitles overlayed
s3 = boto3.resource('s3') #set resource to S3 so that you can delete files from bucket in the next step
bucket = s3.Bucket(outbucket)

# clear the bucket
bucket.objects.all().delete()

#make a thumbnail
thumbnail = Thumbnail.make_thumbnail(Title)

#Remove all .mp4 files after making video


#upload the youtube video
#Google.upload_video('post-final.mp4', thumbnail, Title, mytext + ' : Trawvidsec.net', tags=keywords)
'''args = videoDetails.Video()
youtube = get_authenticated_service()
args.keywords = ''
args.title = Title
args.description = mytext + ' : Trawvidsec.net'
args.category = '28'
args.file = 'post-final.mp4'
try:
    initialize_upload(youtube, args)
except HttpError as e:
    print('An HTTP error %d occurred:\n%s') % (e.resp.status, e.content)'''
