import numpy
import cv2
import os
from PIL import Image
from PIL.ImageChops import invert

def mergeImageGroupVertically(group, path='', limiter='/'):
  # no need to merge on single-image group
  if (len(group) == 1):
    return Image.open(path + limiter + group[0])

  # open all images and read his size
  images = [Image.open(path + limiter + img) for img in group]
  widths, heights = zip(*(img.size for img in images))

  # calulate new size
  total_width = max(widths)
  max_height = sum(heights)

  # generate output image by pasting each one
  new_image = Image.new('RGB', (total_width, max_height))
  y_offset = 0
  for img in images:
    new_image.paste(img, (0,y_offset))
    y_offset += img.size[1]

  return new_image

# used only to remove black and white, red = 0 or = 255
def removeColorByRedChannel(img, redValue):
  # use numpy since it is super-faster than pillow
  data = numpy.array(img)
  red, green, blue, alpha = data.T
  undesired_areas = red == redValue
  # set trasparent pixels
  data[...][undesired_areas.T] = (255, 255, 255, 0)
  return Image.fromarray(data) # back yo pillow format

def getBorderOnlyImage(img):
  img_arr = numpy.asarray(img)
  # determine border size (must be odd!)
  blur = cv2.GaussianBlur(img_arr, (21, 21), 2)
  #h, w = img_arr.shape[:2] # NOTE: seems unused

  # go over edges
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
  gradient = cv2.morphologyEx(blur, cv2.MORPH_GRADIENT, kernel)

  #limit to black and white colors
  lowerb = numpy.array([0, 0, 0])
  upperb = numpy.array([15, 15, 15])
  binary = cv2.inRange(gradient, lowerb, upperb)

  # back to pillow format
  return Image.fromarray(binary).convert('RGBA')

def addBorderToImage(image):
  # prepare images to merge
  fill_image = image
  border_image = getBorderOnlyImage(fill_image)

  # fill must be white, so invert colors
  fill_image = invert(fill_image).convert('RGBA')

  # set trasparent pixels when needed
  fill_image = removeColorByRedChannel(fill_image, 0)
  border_image = removeColorByRedChannel(border_image, 255)

  # merge images
  border_image.paste(fill_image, (0, 0), fill_image)
  return border_image