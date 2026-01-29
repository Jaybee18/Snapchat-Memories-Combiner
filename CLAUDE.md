# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python tool for processing and combining Snapchat exported memories. When Snapchat exports memories, it splits them into:
- **Base files** (`-main.jpg` or `-main.mp4`): The original images or videos
- **Overlay files** (`-overlay.png`): PNG overlays with Snapchat UI elements (text, timestamps, stickers, etc.)

The tool combines matching base and overlay files and provides an interactive interface to choose whether to keep only the combined result or both the combined and original base files.

## Project Structure

- `main.py`: Entry point (currently minimal implementation)
- `memories/`: Directory containing exported Snapchat memories (base and overlay files)
- `out/`: Output directory for processed/combined files
- `pyproject.toml`: Python project configuration using uv/pip standards

## File Naming Convention

Snapchat memories follow this naming pattern:
```
YYYY-MM-DD_<UUID>-main.<ext>     # Base file (jpg/mp4)
YYYY-MM-DD_<UUID>-overlay.png    # Overlay file (png)
```

Matching pairs share the same date and UUID but differ in the suffix:
- `-main.jpg` or `-main.mp4` for base media
- `-overlay.png` for the overlay

## Development Commands

The project uses Python 3.10+ and uv for dependency management.

**Setup:**
```bash
# Create virtual environment
uv venv

# Install dependencies
uv pip install pillow ffmpeg-python
```

**Note:** The `ffmpeg` binary must be installed on your system (not just the Python package). On macOS: `brew install ffmpeg`

**Run the program:**
```bash
python main.py
```

**Reset processing state:**
```bash
rm .processing_state.json
```

## Architecture

### Core Components

1. **MemoryPair**: Represents a base file and its optional overlay, with logic to identify matching pairs by filename
2. **ProcessingState**: Manages JSON-based state persistence for resume functionality (`.processing_state.json`)
3. **File Pairing Logic**: Parses filenames using regex to extract date-UUID prefix and match base/overlay pairs
4. **Image Compositing**: Uses PIL/Pillow to alpha-composite PNG overlays onto JPG base images
5. **Video Compositing**: Uses ffmpeg-python to overlay PNG images onto MP4 videos
6. **Display System**: Opens files in the system's default viewer (macOS: `open`, Linux: `xdg-open`, Windows: `startfile`)

### Processing Flow

1. Scan `memories/` directory and pair files by identifier
2. Load processing state from `.processing_state.json`
3. Filter out already-processed memories
4. For each memory:
   - Combine base + overlay (if overlay exists)
   - Display combined result to user
   - Prompt for user choice (keep combined only, keep both, skip, quit)
   - Save selected files to `out/` directory
   - Mark as processed in state file
5. Support Ctrl+C interruption at any point - progress is saved after each memory

### State Management

The program is fully resumable. If stopped (via 'q', Ctrl+C, or error), simply run `python main.py` again to continue from where you left off. The state file tracks which memories have been processed by their identifier.
