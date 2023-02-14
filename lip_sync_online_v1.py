import os
import sys
import moviepy.editor as mp
from pysrt import SubRipFile, SubRipTime, SubRipItem

def srt_time_to_seconds(time_datetime_format):
    time_iso_format = time_datetime_format.isoformat()
    seconds = float(time_iso_format.split(':')[-1])
    rest_list = time_iso_format.split(':')[:-1]
    if ":".join(rest_list) == "00:00":
        pass
    else:
        for i in range(0,rest_list):
            if i == 0:
                seconds += int(rest_list[i])*3600
            elif i == 1:
                seconds += int(rest_list[i])*60
            else:
                sys.exit("Error in time conversion")
    return seconds

def lip_sync(video_path, srt_path, audio_list, output_video, output_srt):

    # output filename without extension
    output_filename = os.path.splitext(output_video)[0]

    # read srt file
    srt = SubRipFile.open(srt_path)

    # initialize variables
    video_clips = []

    # video_clip_duration_list = []
    # total_video_clip_duration = 0.0
    # warped_video_clip_duration_list = []
    # total_warped_video_clip_duration = 0.0

    # audio_clip_duration_list = []
    # total_audio_clip_duration = 0.0

    # inter_str_clip_position_list = []
    # inter_str_clip_duration_list = []
    # total_inter_str_clip_duration = 0.0

    prev_end_time = SubRipTime(0)

    new_srt_start_time = []
    new_srt_end_time = []
    new_srt_total_duration = 0.0

    # iterate through srt entries
    for i, srt_entry in enumerate(srt):

        # print("--------------------------------")

        start_time = srt_entry.start.to_time()
        end_time = srt_entry.end.to_time()

        # print(f"i: {i}, start_time: {srt_time_to_seconds(start_time)}, end_time: {srt_time_to_seconds(end_time)}, text: {srt_entry.text}, prev_end_time: {srt_time_to_seconds(prev_end_time.to_time())}")

        if srt_time_to_seconds(start_time) > srt_time_to_seconds(prev_end_time.to_time()):
            # add inter-srt clip to video_clips
            # print(f"Adding inter-srt clip to video clips list\nDuration of inter-srt clip: {srt_time_to_seconds(start_time) - srt_time_to_seconds(prev_end_time.to_time())}")
            inter_srt_clip = mp.VideoFileClip(video_path).subclip(srt_time_to_seconds(prev_end_time.to_time()), srt_time_to_seconds(start_time))
            inter_srt_clip_without_audio = inter_srt_clip.without_audio()
            # Create a silent audio clip with the same duration as the video
            silence = mp.afx.audio_loop(mp.AudioFileClip("silence.wav"), duration=(srt_time_to_seconds(start_time) - srt_time_to_seconds(prev_end_time.to_time())), nloops=1)
            # Set the silent audio track in the video clip
            inter_srt_clip_with_silence = inter_srt_clip_without_audio.set_audio(silence)
            video_clips.append(inter_srt_clip_with_silence)
            # Other infos
            # inter_str_clip_position_list.append(i)
            # inter_str_clip_duration_list.append(srt_time_to_seconds(start_time) - srt_time_to_seconds(prev_end_time.to_time()))
            # total_inter_str_clip_duration += (srt_time_to_seconds(start_time) - srt_time_to_seconds(prev_end_time.to_time()))
            new_srt_total_duration += inter_srt_clip_with_silence.duration

        # add srt clip to video_clips
        # print(f"Adding SRT clip to video clips list\nDuration of clip: {srt_time_to_seconds(end_time) - srt_time_to_seconds(start_time)}")
        srt_clip = mp.VideoFileClip(video_path).subclip(srt_time_to_seconds(start_time), srt_time_to_seconds(end_time))
        srt_clip_without_audio = srt_clip.without_audio()
        video_clips.append(srt_clip_without_audio)
        # Other infos
        # video_clip_duration_list.append(srt_time_to_seconds(end_time) - srt_time_to_seconds(start_time))
        # total_video_clip_duration += (srt_time_to_seconds(end_time) - srt_time_to_seconds(start_time))

        # read audio file
        audio_clip = mp.AudioFileClip(audio_list[i])

        # print(f"srt_clip.duration: {srt_clip.duration}, audio_clip.duration: {audio_clip.duration}")

        # interpolate video to match audio duration
        if srt_clip.duration != audio_clip.duration:
            # srt_clip = srt_clip.fx(mp.vfx.speedx, factor=audio_clip.duration/srt_clip.duration)
            # print(f"srt_clip.factor: {audio_clip.duration/srt_clip.duration}")
            srt_clip = srt_clip.fx(mp.vfx.speedx, factor=srt_clip.duration/audio_clip.duration)
            # print(f"srt_clip.factor: {srt_clip.duration/audio_clip.duration}")
            # print("After interpolation")
            # print(f"srt_clip.duration: {srt_clip.duration}, audio_clip.duration: {audio_clip.duration}")
            srt_clip_without_audio = srt_clip.without_audio()
            # warped_video_clip_duration_list.append(srt_clip.duration)
            # total_warped_video_clip_duration += srt_clip.duration

        # audio_clip_duration_list.append(audio_clip.duration)
        # total_audio_clip_duration += audio_clip.duration

        # replace audio in video clip
        video_clip = srt_clip.set_audio(audio_clip)

        new_srt_start_time.append(new_srt_total_duration)
        new_srt_end_time.append(new_srt_total_duration+video_clip.duration)

        new_srt_total_duration += video_clip.duration

        # add video clip to list
        video_clips[-1] = video_clip

        # update previous end time
        prev_end_time = srt_entry.end

    # print("--------------------------------")

    # print(f"video_clip_duration_list: {video_clip_duration_list}\naudio_clip_duration_list:{audio_clip_duration_list}\ninter_srt_clip_position_list: {inter_str_clip_position_list}\ninter_srt_clip_duration_list: {inter_str_clip_duration_list}\nwarped_video_clip_duration_list: {warped_video_clip_duration_list}")
    # print(f"total_video_clip_duration: {total_video_clip_duration}, total_audio_clip_duration: {total_audio_clip_duration}, total_inter_srt_clip_duration: {total_inter_str_clip_duration}, total_warped_video_clip_duration: {total_warped_video_clip_duration}, final_output_duration: {total_warped_video_clip_duration+total_inter_str_clip_duration}, expected_output_duration: {total_audio_clip_duration+total_inter_str_clip_duration}")

    # print("--------------------------------")

    # check if last srt ends before video ends and add final clip if necessary
    last_srt_end_time = srt[-1].end.to_time()
    video_duration = mp.VideoFileClip(video_path).duration
    if last_srt_end_time != video_duration:
        final_clip = mp.VideoFileClip(video_path).subclip(srt_time_to_seconds(last_srt_end_time), video_duration)
        final_clip_without_audio = final_clip.without_audio()
        # Create a silent audio clip with the same duration as the video
        silence = mp.afx.audio_loop(mp.AudioFileClip("silence.wav"), duration=(video_duration - srt_time_to_seconds(last_srt_end_time)), nloops=1)
        final_clip_with_silence = final_clip_without_audio.set_audio(silence)
        video_clips.append(final_clip_with_silence)
        # video_clips.append(final_clip_without_audio)

    # concatenate video clips and write final video
    final_video = mp.concatenate_videoclips(video_clips)
    # final_video.write_videofile("output_video.mp4", threads=30)
    final_video.write_videofile(output_video, verbose=False, codec="libx264", threads=30, audio_codec='aac', temp_audiofile=output_filename+'.m4a', remove_temp=True, preset="medium", ffmpeg_params=["-profile:v","baseline", "-level","3.0","-pix_fmt", "yuv420p"])

    # create new srt file with updated timings
    new_srt = SubRipFile()
    for i, srt_entry in enumerate(srt):
        new_start_time = SubRipTime(seconds=new_srt_start_time[i])
        new_end_time = SubRipTime(seconds=new_srt_end_time[i])
        new_srt.append(SubRipItem(index=i+1, start=new_start_time, end=new_end_time, text=srt_entry.text))

    # Write the updated srt file to file
    new_srt.save(output_srt, encoding='utf-8')

if __name__ == "__main__":
    # input file paths
    video_path = "test_data/video.mp4"
    srt_path = "test_data/subs.srt"
    audio_dir = "test_data/audio_1min"
    output_video = "test_data/output_video.mp4"
    output_srt = "test_data/output_video.srt"

    audio_list = os.listdir(audio_dir)
    audio_list = [os.path.join(audio_dir, file) for file in audio_list]

    lip_sync(video_path, srt_path, audio_list, output_video, output_srt)
