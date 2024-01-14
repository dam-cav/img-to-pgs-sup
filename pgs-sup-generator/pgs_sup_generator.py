import re
import argparse
import pytesseract
import multiprocessing
import platform

from lib.image_manipulation import *
from lib.sub_manipulation import *

LIMITER = "\\" if platform.system() == "Windows" else '/'

def filterWithTesseract(path, file, tesseract):
  pytesseract.pytesseract.tesseract_cmd = tesseract

  try:
    im = Image.open(path + LIMITER + file)
  except IOError:
    print("cannot open image '%s'" % filename)

  ocr = pytesseract.image_to_string(im)
  ocr_match = re.search('.*[a-z].*', ocr)

  if not ocr_match:
    return None
  return file

def main():
  parser = argparse.ArgumentParser(description='Image directory to PGS SUP file generator.')

  parser.add_argument("-p",  "--path",      help="image directory path",  default=".")
  parser.add_argument("-wi", "--width",     help="video width in px",     default="1280")
  parser.add_argument("-he", "--height",    help="video height in px",    default="720")
  parser.add_argument("-o",  "--outfile",   help="output filename",       default="sub.sup")
  parser.add_argument("-t",  "--tesseract", help="tesseract binary path", default=None)

  ARGS = parser.parse_args()
  # NOTE: do not exceed with size since PGS data block is very limited
  sizelimit = int(ARGS.width), int(ARGS.height)

  dir_list = os.listdir(ARGS.path)
  dir_list = [file for file in dir_list if not not re.match('[0-9]{1,2}_[0-9]{1,2}_[0-9]{1,2}_[0-9]{1,3}__[0-9]{1,2}_[0-9]{1,2}_[0-9]{1,2}_[0-9]{1,3}_[0-9]+.(jpe?g|png)', file)]
  dir_list.sort()

  counter = 0
  sub = b''
  time_groups = {}

  for file in dir_list:
    time_match = re.search(
      '([0-9]{1,2})_([0-9]{1,2})_([0-9]{1,2})_([0-9]{1,3})__([0-9]{1,2})_([0-9]{1,2})_([0-9]{1,2})_([0-9]{1,3})_[0-9]+.(jpe?g|png)',
      file
    )

    start_time = (int(time_match.group(1)) * 60 * 60 * 1000 * 90) \
      +  (int(time_match.group(2)) * 60 * 1000 * 90) \
      +  (int(time_match.group(3)) * 1000 * 90) \
      +  (int(time_match.group(4)) * 90)
    end_time = (int(time_match.group(5)) * 60 * 60 * 1000 * 90) \
      +  (int(time_match.group(6)) * 60 * 1000 * 90) \
      +  (int(time_match.group(7)) * 1000 * 90) \
      +  (int(time_match.group(8)) * 90)

    key = "{start}_{end}".format(start=start_time, end=end_time)
    if not time_groups.get(key):
      time_groups[key] = []

    time_groups[key].append(file)

  for group_key in time_groups:
    print('Doing group:', group_key)

    group = time_groups[group_key]

    if ARGS.tesseract:
      # NOTE slowest part, make it multithread
      a_pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count()-1) or 1)
      group = a_pool.starmap(filterWithTesseract, [(ARGS.path, file, ARGS.tesseract) for file in group])
    group = list(filter(None, group))

    if len(group) == 0:
      # no remaining images
      continue

    image = mergeImageGroupVertically(group, path=ARGS.path, limiter=LIMITER)
    image = image.convert('RGB')
    image = addBorderToImage(image)

    time_match = re.search(
      '([0-9]+)_([0-9]+)',
      group_key
    )

    start_time = int(time_match.group(1))
    end_time   = int(time_match.group(2))

    sub += generateFrame(file, image, start_time, end_time, counter, sizelimit)
    counter += 1

  with open(ARGS.outfile, "wb") as f:
  	f.write(sub)

if __name__ == "__main__":
  multiprocessing.freeze_support()
  main()