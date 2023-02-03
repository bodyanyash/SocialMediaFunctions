from VidMaker.MyFunctions import *





# headers = get_api_headers()
# StockInfo = get_stock_info_api(headers, 'TSM')
# file = makedailygraph(StockInfo)
# print(file)
# '''

gainers_page = get_content_soup('https://finance.yahoo.com/gainers/')
losers_page = get_content_soup('https://finance.yahoo.com/losers/')
gain_stock_info = get_stock_info_soup(gainers_page)
loss_stock_info = get_stock_info_soup(losers_page)
Type1 = 'Gain'
Type2 = 'Loss'
AllStocks = {Type1: gain_stock_info, Type2: loss_stock_info}
print(AllStocks)
Ranges = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
Intervals = ['1m', '2m', '5m', '15m', '60m', '1d']
headers = get_api_headers()
Ranger = '5d'
Interval = getInterval(Ranger)

global region, inbucket, outbucket
region = 'us-east-1'
outbucket = inbucket = 'justin-speech-synthesis-bucket'
outfiletype = 'mp3'
outlang = 'en-US'
print(AllStocks[Type1])

infile = ''
outfilename = ''
#data = get_stock_summary(headers, 'PSNYW')
#print(json.loads(data)['summaryProfile'])

mytext = 'This business has no summary'
for i in AllStocks[Type1]:
    symbol = i['Symbol']
    name = symbol + '/' + 'temp.mp4'
    StockGraphData = get_stock_info_api(headers, symbol, Ranger, Interval)
    # print(StockGraphData)
    if len(json.loads(StockGraphData)["chart"]["result"][0]["indicators"]["quote"][0]['close']) < 4:
        pass
    else:
        file, file2 = makegraph(StockGraphData)
        # print(file)

        StockStats = get_stock_statistics(headers, symbol)
        # print(StockStats)
        # print(i)
        data = get_stock_summary(headers, symbol)
        if 'longBusinessSummary' in json.loads(data)['summaryProfile']:
            mytext = json.loads(data)['summaryProfile']['longBusinessSummary']
        else:
            pass

        keywords = getkeywords(mytext)
        print('keywords: ', keywords)
        #print(StockStats)
        file3 = prepare_speech(StockStats, i, mytext)
        print('prepare_speech successful: ', file3)
        try:
            shutil.rmtree(symbol)
        except (RuntimeError, TypeError, NameError, FileNotFoundError):
            pass
        os.mkdir(symbol)
        os.rename(file3, symbol + '/' + file3)
        os.rename(file2, symbol + '/' + file2)
        os.rename(file, symbol + '/' + file)
        print(file, file2, file3)
        combine = combineAudioVideo(symbol + '/' + file, symbol + '/' + file2)
        # combine = symbol + '/' + combine
        assets = []
        for keyw in keywords:
            assets = assets + PexelsAssets(keyw, 'photo', 0)
            assets = assets + PexelsAssets(keyw, 'video', 1)
        assets = list(set(assets))
        #assets = ['blinds0.mp4', 'addition0.mp4', 'ceramic0.mp4', 'contractors0.mp4']
        half1 = Montage(assets, symbol + '/' + file3, symbol + '/' + 'montage.mp4')
        print('montaged')
        final = concatenate_videoclips([half1, combine.resize((1920, 1080))])
        final.write_videofile(name)
        audio = concatenate_audioclips([AudioFileClip(symbol + '/' + file3), AudioFileClip(symbol + '/' + file2)])  # 3.
        scriptVoice = 'script.mp3'
        audio.write_audiofile(scriptVoice)  # 4.
        upload_file(scriptVoice, inbucket)
        response = createTranscribeJob(region, inbucket, scriptVoice)
        while (response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
            print("."),
            time.sleep(30)
            response = getTranscriptionJobStatus(response["TranscriptionJob"]["TranscriptionJobName"])
        transcript = getTranscript(str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]))
        writeTranscriptToSRT(transcript, 'en', "subtitles-en.srt")
        createSubbedClip(name, "subtitles-en.srt", symbol + '/' + 'final.mp4', "audio-en.mp3", True)

        # final = concatenate_videoclips([VideoFileClip(half1), VideoFileClip(combine).resize((1920,1080))])
        # final.write_videofile(symbol+'/'+'final.mp4')
        #for asset in assets:
        #    os.remove(asset)
        break

'''
for stock in AllStocks[Type1]:
    print('stock:', stock)
    StockInfo = get_stock_info_api(headers, stock['Symbol'], Ranger, Interval)
    file = makegraph(StockInfo)
    print(file)
# prepare_speech(AllStocks)
# use_polly('New Speech','yes','Justin');
# '''
