#!/usr/bin/env python3
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image
import ffmpeg


# Directories
MEMORIES_DIR = Path("memories")
OUTPUT_DIR = Path("out")
BASES_DIR = Path("bases")


class MemoryPair:
    """Represents a base file and its optional overlay."""

    def __init__(self, base_path: Path, overlay_path: Optional[Path] = None):
        self.base_path = base_path
        self.overlay_path = overlay_path
        self.is_video = base_path.suffix.lower() in ['.mp4', '.mov']

    def __repr__(self):
        return f"MemoryPair({self.base_path.name}, overlay={self.overlay_path.name if self.overlay_path else None})"


def scan_memories() -> List[MemoryPair]:
    """Scan the memories directory and pair base files with overlays."""
    if not MEMORIES_DIR.exists():
        print(f"Error: {MEMORIES_DIR} directory not found")
        sys.exit(1)

    # Group files by their identifier (date_uuid)
    files_by_id: Dict[str, Dict[str, Path]] = {}

    for file_path in MEMORIES_DIR.iterdir():
        if not file_path.is_file():
            continue

        # Parse filename: YYYY-MM-DD_UUID-TYPE.ext
        match = re.match(r'(.+?)-(main|overlay)\.(\w+)$', file_path.name)
        if not match:
            continue

        identifier, file_type, _ = match.groups()

        if identifier not in files_by_id:
            files_by_id[identifier] = {}

        files_by_id[identifier][file_type] = file_path

    # Create MemoryPair objects
    pairs = []
    for identifier, files in sorted(files_by_id.items()):
        if 'main' in files:
            overlay = files.get('overlay')
            pairs.append(MemoryPair(files['main'], overlay))

    return pairs


def combine_image(base_path: Path, overlay_path: Path, output_path: Path):
    """Combine base image with overlay using PIL."""
    base = Image.open(base_path)
    overlay = Image.open(overlay_path).convert("RGBA")

    # Preserve EXIF data from base image
    exif = base.info.get('exif')

    # Resize overlay to match base if needed
    if base.size != overlay.size:
        overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)

    # Convert base to RGBA for compositing
    if base.mode != 'RGBA':
        base = base.convert('RGBA')

    # Composite the images
    combined = Image.alpha_composite(base, overlay)

    # Convert back to RGB for JPEG output
    if output_path.suffix.lower() in ['.jpg', '.jpeg']:
        combined = combined.convert('RGB')

    # Save with EXIF data if available
    if exif:
        combined.save(output_path, quality=95, exif=exif)
    else:
        combined.save(output_path, quality=95)

    # Copy file timestamps from original
    stat = os.stat(base_path)
    os.utime(output_path, (stat.st_atime, stat.st_mtime))


def combine_video(base_path: Path, overlay_path: Path, output_path: Path):
    """Combine base video with overlay using ffmpeg."""
    input_video = ffmpeg.input(str(base_path))
    input_overlay = ffmpeg.input(str(overlay_path))

    # Get video info to scale overlay to match
    probe = ffmpeg.probe(str(base_path))
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])

    # Scale overlay to match video dimensions, then overlay at 0,0
    scaled_overlay = ffmpeg.filter(input_overlay, 'scale', width, height)
    video_output = ffmpeg.filter([input_video, scaled_overlay], 'overlay', x='0', y='0')
    
    # Check if video has audio stream
    has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])

    if has_audio:
        audio_output = input_video.audio
        output = ffmpeg.output(video_output, audio_output, str(output_path),
                              vcodec='libx264', acodec='copy', pix_fmt='yuv420p',
                              **{'map_metadata': 0})
    else:
        output = ffmpeg.output(video_output, str(output_path),
                              vcodec='libx264', pix_fmt='yuv420p',
                              **{'map_metadata': 0})

    # Run ffmpeg
    ffmpeg.run(output, overwrite_output=True)

    # Copy file timestamps from original
    stat = os.stat(base_path)
    os.utime(output_path, (stat.st_atime, stat.st_mtime))


def main():
    print("Snapchat Memories Batch Combiner")
    print("="*60)

    # Create output directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    BASES_DIR.mkdir(exist_ok=True)

    # Scan for memory pairs
    print("Scanning memories directory...")
    pairs = scan_memories()
    print(f"Found {len(pairs)} memory files\n")

    # Process all pairs
    for i, pair in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] Processing: {pair.base_path.name}")

        # Copy base to bases directory (copy2 preserves timestamps)
        base_copy = BASES_DIR / pair.base_path.name
        shutil.copy2(pair.base_path, base_copy)

        # Combine with overlay if present
        if pair.overlay_path:
            combined_name = pair.base_path.name.replace('-main', '-combined')
            combined_path = OUTPUT_DIR / combined_name

            if pair.is_video:
                combine_video(pair.base_path, pair.overlay_path, combined_path)
            else:
                combine_image(pair.base_path, pair.overlay_path, combined_path)

            print(f"  → Combined: {combined_path.name}")
        else:
            print(f"  → No overlay found, skipped combination")

        print(f"  → Base saved: {base_copy.name}")
        print()

    # Summary
    print("="*60)
    print(f"Processing complete!")
    print(f"\nCombined files: {OUTPUT_DIR}/")
    print(f"Original bases: {BASES_DIR}/")


if __name__ == "__main__":
    main()
