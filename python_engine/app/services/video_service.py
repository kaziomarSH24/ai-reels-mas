import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VideoService:
    def __init__(self):
        # Base directory to store generated reels (shared volume with Laravel)
        self.output_dir = Path("/var/www/public/reels")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_and_crop_clip(self, source_url: str, start_time: str, duration: int, output_filename: str) -> str:
        """
        Extracts a specific portion of a video from a remote URL or local path,
        and crops it to 9:16 (vertical/reels format).
        
        Args:
            source_url (str): The direct URL or path to the source video (.mp4).
            start_time (str): The start time in 'HH:MM:SS' format (e.g., '00:01:15').
            duration (int): Duration in seconds to cut (e.g., 10).
            output_filename (str): Desired output filename (e.g., 'reel_123.mp4').
            
        Returns:
            str: Path to the generated output file, or raises an Exception.
        """
        output_path = self.output_dir / output_filename
        
        # If output file already exists, remove it
        if output_path.exists():
            output_path.unlink()

        logging.info(f"Starting video extraction. Source: {source_url} | Start: {start_time} | Duration: {duration}s")

        # FFmpeg Command Breakdown:
        # -ss : Seeks to the start time (placed before -i for fast seeking)
        # -i  : Input file or URL
        # -t  : Duration to cut
        # -vf "crop=ih*(9/16):ih" : Crops the video to 9:16 ratio (centered)
        # -c:a aac : Re-encodes audio to aac for compatibility
        # -c:v libx264 : Re-encodes video using standard H.264
        
        command = [
            "ffmpeg",
            "-y",                     # Overwrite output files without asking
            "-ss", start_time,        # Fast seek to start time
            "-i", source_url,         # Input source
            "-t", str(duration),      # Duration
            "-vf", "crop=ih*(9/16):ih", # Crop to 9:16 Mobile Aspect Ratio
            "-c:v", "libx264",        # Video codec
            "-preset", "fast",        # Encoding speed preset
            "-c:a", "aac",            # Audio codec
            "-b:a", "192k",           # Audio bitrate
            "-strict", "experimental",
            str(output_path)
        ]

        try:
            # Execute the FFmpeg command
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Check if FFmpeg succeeded
            if process.returncode != 0:
                logging.error(f"FFmpeg Error: {process.stderr}")
                raise RuntimeError(f"FFmpeg failed with exit code {process.returncode}")

            logging.info(f"Successfully created reel: {output_path}")
            return str(output_path)

        except Exception as e:
            logging.error(f"Video Processing Exception: {str(e)}")
            raise e
