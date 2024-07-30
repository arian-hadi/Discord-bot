import requests,json
from apikey import url, API_KEY, base_video_url
import logging
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_api():
    response = requests.get(url)
    result = response.json()
    return result

def check_new_video():
    # Make a request to the YouTube API to check for a new video
    result = get_api()
    video_id = result['items'][0]['id']['videoId']
    channel_title = result['items'][0]['snippet']['channelTitle']
    title = result['items'][0]['snippet']['title']
    
    
    with open("data/YouTubedata.json","w") as f:
        json.dump(result, f)
    try:       
        with open("data/video_id.json", "r") as read_file:
            json_data = json.load(read_file)
        json_value = json_data["video_id"]
        logger.info(f"json_value: {json_value}")
        logger.info(f"Video_id : {video_id}")
        logger.info(f"channel title: {channel_title}")
        logger.info(f"description: {title}")

        if json_value == video_id:
            return None,None,channel_title,title
        
        with open("data/video_id.json", "w") as file:
            json.dump({"video_id": video_id}, file)
        return base_video_url + video_id, video_id, channel_title,title
    except Exception as e:
        logger.info(f"An error occured, type error: {e}")


youtube = build("youtube", "v3", developerKey=API_KEY)
def get_pfp(youtube_id):
    request = youtube.channels().list(
        part = "snippet",
        id = youtube_id
    )
    response = request.execute()
    channel_pfp = response['items'][0]['snippet']['thumbnails']['default']['url']
    return channel_pfp
