import subprocess
import os

# === INPUT FILE PATHS ===

# Path to the original movie (must be a real .mkv or .mp4 file)
original_path = "/home/rickoserver/media/movies/Avatar (2009)/Avatar.2009.1080p.mkv"

# Path to the new audio file (must be a real .mka, .aac, .ac3, or .mp3 audio file)
new_audio_path = "/home/rickoserver/downloads/spanish_audio.mka"

# Output file path (this is the final merged movie with both audio tracks)
output_path = "/home/rickoserver/media/movies/Avatar (2009)/Avatar.2009.1080p.with.spanish.mkv"

# === FFMPEG COMMAND ===
# -map 0 means keep everything from the first input (video, original audio, subtitles)
# -map 1:a means take audio track(s) from second input
# -c copy means do not re-encode (fast and lossless)

cmd = [
    "ffmpeg",
    "-i", original_path,
    "-i", new_audio_path,
    "-map", "0",
    "-map", "1:a",
    "-c", "copy",
    output_path
]

# === RUN THE COMMAND ===
print("🛠️ Injecting new audio with ffmpeg...")
try:
    subprocess.run(cmd, check=True)
    print(f"✅ Done! New file saved as:\n{output_path}")
except subprocess.CalledProcessError as e:
    print("❌ FFmpeg failed:", e)

def inject_audio_track(video_path, audio_path, output_path):
    print(f"🛠 Injecting audio...\n🎞 {video_path}\n🔊 {audio_path}\n💾 {output_path}")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0",
        "-map", "1:a",
        "-c", "copy",
        output_path
    ]
    subprocess.run(cmd, check=True)
    print("✅ Injection complete")
