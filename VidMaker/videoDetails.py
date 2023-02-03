import os
from googleapiclient.http import MediaFileUpload

class Video:
    description = "test description"
    category = "22"
    keywords = "test"
    privacyStatus = "public"
    title = 'Title'
    file = 'post-final.mp4'

    def getFileName(self, type):
        for file in os.listdir("."):
            if type == "video" and file.split(".", 1)[1] != "jpg":
                return file
                break
            elif type == "thumbnail" and file.split(".", 1)[1] != "mp4":
                return file
                break

    def insertThumbnail(self, youtube, videoId):
        thumbnailPath = "pil_text_font.png"

        request = youtube.thumbnails().set(
            videoId=videoId,
            media_body=MediaFileUpload(thumbnailPath)
        )
        response = request.execute()
        print(response)
