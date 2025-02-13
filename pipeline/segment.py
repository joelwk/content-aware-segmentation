from segment_averaging import main as segment_averaging_main
from move_and_group import main as move_and_group_main
from save_to_webdataset import package_datasets_to_webdataset_segmentation
from whisper import main as whisper_main
from successor_segmentation import SegmentSuccessorAnalyzer, run_analysis
from fold_seams import main as fold_seams_main
from utils import convert_types, rename_and_move, move_or_copy_files
import os
import shutil
from pipeline import read_config, string_to_bool

configs = read_config()
directories = read_config(section="directory")
configs = read_config(section="config_params")
evaluations = read_config(section="evaluations")

def remove_incomplete_video_directories():
    required_dirs = [directories['keyframe_audio_clip_output'], directories['embeddings'], directories['keyframes'], directories['original_frames']]
    base_dir = evaluations['completedatasets']
    for video_dir in os.listdir(base_dir):
        video_path = os.path.join(base_dir, video_dir)
        if not os.path.isdir(video_path):
            continue
        missing_or_empty = any(not os.path.exists(os.path.join(video_path, req_dir)) or not os.listdir(os.path.join(video_path, req_dir)) for req_dir in required_dirs)
        if missing_or_empty:
            shutil.rmtree(video_path)
            print(f"Removed incomplete or empty directory: {video_path}")

def run_all_scripts():
    segment_video = string_to_bool(configs.get("segment_video", "False"))
    segment_audio = string_to_bool(configs.get("segment_audio", "True"))
    specific_videos_str = configs.get("specific_videos", "")
    specific_videos = [int(x.strip()) for x in specific_videos_str.strip('[]').split(',')] if specific_videos_str and specific_videos_str != "None" else None
    try:
        print('Running rename_and_move')
        rename_and_move()
        run_analysis(SegmentSuccessorAnalyzer)
        print('Running successor segmentation')
        fold_seams_main(segment_video, segment_audio, specific_videos)
        segment_averaging_main()
        print('Running move_and_group')
        move_and_group_main()
        remove_incomplete_video_directories()
        print('Running process_audio_files')
        whisper_main()
        print('Running convert_types')
        convert_types()
        print('Running save_to_webdataset')
        move_or_copy_files()
        package_datasets_to_webdataset_segmentation()
    except Exception as e:
        print(f"An error occurred in the pipeline: {e}")

def initialize_and_run():
    try:
        run_all_scripts()
    except FileNotFoundError as e:
        print(f"File or directory not found: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    initialize_and_run()