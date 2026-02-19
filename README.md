# Snapchat Memories Combiner

**This script does not download anything! It just processes your files**

This script combines the "-main" files with their respective "-overlay" files you get from exporting your memories from Snapchat.

## Usage
Extract the .zip file(s) you got from Snapchat. There should be a `memories/` folder in each of them (Sometimes you get more than one zip).

Move all of the images and videos into a single `memories/` folder in the same directory as the `main.py` file.

Open a terminal in the same directory and run the script with `uv run main.py`. (If you don't have uv, install it from [here](https://docs.astral.sh/uv/getting-started/installation/))

All base files (those that didn't have overlays **and** those that did) will be placed in a `bases/` folder. All files that had overlays are combined and placed in `out/`. 

This means that there are "duplicates" that are in both folders (base in `base/` and base with overlay in `out/`), but I'll let you decide what to do with them (or use --cleanup to remove them automatically).

## Flags

### `--cleanup`
After processing, removes all overlay files and their corresponding main files
from the `memories/` directory, and deletes the `bases/` directory.
Only files that were successfully combined (i.e. had an overlay) are removed —
files without overlays are left untouched.

You will be asked to confirm before anything is deleted.
```bash
uv run main.py --cleanup
```
