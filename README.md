# Images to PGS SUP subtitle

PGS SUP subtitle generator (Image sequences)

It generates subtitles starting from a series of white-background black-content  images (`png/jpg` format)

Each image must have the name in the format
`HH_mm_ss_SSS__HH_mm_ss_SSS_XXXXX.extension`, where:

- the first `HH_mm_ss_SSS` is the start time
- the last `HH_mm_ss_SSS` is the end time
- `XXXXX` is the sequence number

A script to correct times and durations is included in the project.

# FAQ

## Why not simply use an OCR to generate an SRT file?

- You don't always have to do with well defined images
- You don't always have to do with images containing text

When you can, prefer subtitles in text format (like SRT)

## If you don't want to use an OCR, why is there a "tesseract" option?

If you have a list of images and not all of them include texts, you may want to filter those in which tesseract manages to recognize at least one character of the alphabet

## How are the images coded inside the PGS SUP file?

Refer to  "Method for run-length encoding of a bitmap data stream", you can also find a summary in the `/docs` folder of the project

# Usage

```
usage: pgs_sup_generator.py [-h] [-p PATH] [-wi WIDTH] [-he HEIGHT] [-o OUTFILE] [-t TESSERACT]

Image directory to PGS SUP file generator.

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  image directory path
  -wi WIDTH, --width WIDTH
                        video width in px
  -he HEIGHT, --height HEIGHT
                        video height in px
  -o OUTFILE, --outfile OUTFILE
                        output filename
  -t TESSERACT, --tesseract TESSERACT
                        tesseract binary path
```

```
usage: pgs_sup_retimer.py [-h] [-i INPUT] [-o OUTPUT] [-s SUM] [-m MULTIPLY]

PGS SUP file subtitle timing bulk changer.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        sup input path
  -o OUTPUT, --output OUTPUT
                        sup output path
  -s SUM, --sum SUM     sum given milliseconds (even negative)
  -m MULTIPLY, --multiply MULTIPLY
                        mupltiply times for given value
```