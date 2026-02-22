# Snapchat Memories Combiner

**This script does not download anything! It just processes your files**

This script combines the "-main" files with their respective "-overlay" files you get from exporting your memories from Snapchat.

## Usage
Extract the .zip file(s) you got from Snapchat. There should be a `memories/` folder in each of them (Sometimes you get more than one zip).

Move all of the images and videos into a single `memories/` folder in the same directory as the `main.py` file.

Open a terminal in the same directory and run the script with `uv run main.py`. (If you don't have uv, install it from [here](https://docs.astral.sh/uv/getting-started/installation/))

All output files will be placed in an `out/` folder. Base files that have no overlays will just be copied over. File with overlays will be combined with their respective overlays and the combined version will be placed in `out/`.

You can specify the `--include-bases` flag to also copy the uncombined bases to `out/`.
