from google import genai
from pydantic import BaseModel
from moviepy import *
import tempfile
from youtube_transcript_api import YouTubeTranscriptApi
import pickle


class Commentary(BaseModel):
    """I guess we don't need commentary but still"""
    event_commentary: str
    start_time : float
    end_time : float


def get_commentaries_from_transcription(transcription:str):
    """get relevant commentaries from transcription"""
    client = genai.Client(api_key="")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Given the transcription of a sports game, I want to get highlights by extracting short commentaries(4-5 sentences) for the 20 most relevant key events from the introduction and start of the game to the end. So merge and give commentaries for each key event. Never rephrase. Return the commentary, start time and end time for each key event.\ntranscription: {transcription}",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Commentary],
        },
    )
    return response


def merge_clips(path:str,highlights:list[Commentary]):
    video = VideoFileClip(path)
    clips = [video.subclipped(int(k.start_time), int(k.end_time)) for k in highlights]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile("merged_clip.mp4", codec="libx264", audio_codec="aac")
    

if __name__ == "__main__":
    ytt_api = YouTubeTranscriptApi()
    transcription = ytt_api.fetch("yphmShedwgs")
    # print(transcription)
    # with open("trans.pkl", "wb") as f:
    #      pickle.dump(transcription, f)
         
    # with open("trans.pkl", "rb") as f:  
    #     transcription = pickle.load(f)
    
    temp = []
    for seg in transcription:
        temp.append({"text":seg.text,"start":seg.start, "end":seg.start+seg.duration})
    
    response = get_commentaries_from_transcription(transcription)
    final_response = response.parsed
    
    # with open("commentaries.pkl", "wb") as f:
    #     pickle.dump(final_response, f)
    
    # with open("commentaries.pkl", "rb") as f:  
    #     final_response = pickle.load(f)
    
    # for k in final_response:   
    #     print(k.event_commentary)
    #     print(k.start_time)
    #     print(k.end_time)
        
    merge_clips("sports.mp4",final_response)
