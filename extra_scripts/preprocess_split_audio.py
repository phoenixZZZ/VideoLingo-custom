import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich import print as rprint
import subprocess

# from core.config_utils import load_key
from core.all_whisper_methods.demucs_vl import demucs_main
# from core.all_whisper_methods.audio_preprocess import process_transcription, split_audio, save_results, compress_audio, CLEANED_CHUNKS_EXCEL_PATH
# from core.step1_ytdlp import find_video_files

DEMUCS=True
VIDEO_FILE_PATH="./videos/06-10.mp4"
AUDIO_DIR = "./audio"
RAW_AUDIO_FILE = os.path.join(AUDIO_DIR, "raw.mp3")
VOCAL_AUDIO_FILE = os.path.join(AUDIO_DIR, "vocal.mp3")
# WHISPER_FILE = "output/audio/for_whisper.mp3"
ENHANCED_VOCAL_PATH = "./audio/enhanced_vocals.mp3"

def convert_video_to_audio(video_file: str):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    if not os.path.exists(RAW_AUDIO_FILE):
        print(f"🎬➡️🎵 Converting to high quality audio with FFmpeg ......")
        subprocess.run([
            'ffmpeg', '-y', '-i', video_file, '-vn',
            '-c:a', 'libmp3lame', '-b:a', '128k',
            '-ar', '32000',
            '-ac', '1', 
            '-metadata', 'encoding=UTF-8', RAW_AUDIO_FILE
        ], check=True, stderr=subprocess.PIPE)
        print(f"🎬➡️🎵 Converted <{video_file}> to <{RAW_AUDIO_FILE}> with FFmpeg\n")

def enhance_vocals(vocals_ratio=2.50):
    """Enhance vocals audio volume"""
    if not DEMUCS:
        return RAW_AUDIO_FILE
        
    try:
        print(f"[cyan]🎙️ Enhancing vocals with volume ratio: {vocals_ratio}[/cyan]")
        ffmpeg_cmd = (
            f'ffmpeg -y -i "{VOCAL_AUDIO_FILE}" '
            f'-filter:a "volume={vocals_ratio}" '
            f'"{ENHANCED_VOCAL_PATH}"'
        )
        subprocess.run(ffmpeg_cmd, shell=True, check=True, capture_output=True)
        
        return ENHANCED_VOCAL_PATH
    except subprocess.CalledProcessError as e:
        print(f"[red]Error enhancing vocals: {str(e)}[/red]")
        return VOCAL_AUDIO_FILE  # Fallback to original vocals if enhancement fails
    
def preprocess_split_audio():    
    # step0 Convert video to audio
    video_file = VIDEO_FILE_PATH
    print("video_file:", video_file)
    convert_video_to_audio(video_file)

    # step1 Demucs vocal separation:
    if DEMUCS:
        demucs_main(AUDIO_DIR)
    
    # step2 人声增强
    choose_audio = enhance_vocals() if DEMUCS else RAW_AUDIO_FILE
    # whisper_audio = compress_audio(choose_audio, WHISPER_FILE)

    # # step3 Extract audio
    # segments = split_audio(whisper_audio)
    
        
if __name__ == "__main__":
    preprocess_split_audio()