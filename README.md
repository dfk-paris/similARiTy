# Requirements

* python >= 3.2
* ImageMagick >= 7

# Installation

    git clone https://github.com/dfk-paris/similARiTy
    cd similARiTy
    pip install -r requirements.txt

# Usage

Basically, you first create an “index” for a given directory. This creates a
json file. Do this for two directories and then compare the json files, e.g.:

    bin/similar index /path/to/base_set base.json
    bin/similar index /path/to/other_set other.json
    bin/similar compare base.json other.json out.html

To list available sub commands, please run

    bin/similar --help

and then show more specific help for each sub command with e.g.

    bin/similar index --help

# Hints

* Indexing is a lot faster if input images are small. A bounding box of 80x80
  pixel is a good choice since it still allows to recognize the images in the
  html output.
* The default is the dhash with max distance 15. If you switch to phash, make
  sure to also reduce the distance, since the phash is only half the size of
  the dhash (64 bit vs 128 bit).
* phash is faster to compare since it is shorter than dhash.
