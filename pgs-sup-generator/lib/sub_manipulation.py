from PIL import Image

PG_ESCAPE = ('PG').encode('utf-8')
PG_SEGMENT_TYPE = {
  'PCS': b'\x16',
  'WDS': b'\x17',
  'PDS': b'\x14',
  'ODS': b'\x15',
  'END': b'\x80',
}

# order is not casual, pay attention!
COLORS = [
  b'\x10\x80\x80\x00', # 0 - transparent
  b'\xff\x7f\x7f\xff', # 1 - white
  b'\x00\x7f\x7f\xff', # 2 - black
]

def paletteCodeNumber(pixel):
  if pixel[1] == 0:
    return 0 # 'transparent'
  if pixel[0] == 0:
    return 2 # 'black'
  return 1 # 'white'

def numberToHexBytes(number, lenght):
  # every hex char is 2-char long
  lenght = lenght * 2
  hex_string = hex(number).split('x')[1]
  if len(hex_string) < lenght:
    hex_string = ('0' * (lenght - len(hex_string))) + hex_string
  return bytes.fromhex(hex_string)

def toColorCode(colorcode, count):
  # return noting on no repetitions
  if count == 0:
    return b''
  # single pixel on non-base color (non-zero)
  if count == 1 and colorcode != 0:
    return numberToHexBytes(colorcode, 1)

  structure = b'\x00' # default escape character
  if count <= 63:
    # 0     - 00 LL LL LL
    # 128   - 10 LL LL LL
    structure += numberToHexBytes((count + 0) if colorcode == 0 else (count + 128), 1)
  elif count <= 16383:
    # 16384 - 01 LL LL LL  LL LL LL LL
    # 49152 - 11 LL LL LL  LL LL LL LL
    structure += numberToHexBytes((count + 16384) if colorcode == 0 else (count + 49152), 2)
  else:
    # generate one of max size
    # missing 'count' will be passed to next block
    structure = toColorCode(colorcode, 16383)

  # need to specify color in case of non-base
  if colorcode != 0:
    structure += numberToHexBytes(colorcode, 1)
  if count > 16383:
    # recursively pass missing 'count' to next block
    structure += toColorCode(colorcode, count - 16383)
  return structure

def toSubData(image, colors, size):
  data = bytes([])
  lastcolor = None
  colorcode = None
  # reduce sub image to screen limit
  image.thumbnail(size)
  # reduce number of colors (LA = scale of grey with alpha-channel)
  image = image.convert('LA', dither=Image.NONE)
  wid = image.width
  hei = image.height

  # same color pixel counter
  count = 0
  # current horizontal line pixel counter
  linewidth_count = 0

  # count pixel form left to right, top to bottom
  for pixel in iter(image.getdata()):
    cycleColor = paletteCodeNumber(pixel)

    if lastcolor == cycleColor and linewidth_count < wid:
      # same color as before and horizontal line no ended
      count += 1
    else:
      # different color or line ended

      if lastcolor != None:
        #write counted pixels (skipped on first cicle)
        data += toColorCode(lastcolor, count)

      # reset counters for next sum
      count = 1
      lastcolor = cycleColor

    linewidth_count += 1

    if linewidth_count > wid:
      # line end delimiter
      data += b'\x00\x00'
      linewidth_count = 1

  # write last cycle color (since you will not found a different one next)
  data += toColorCode(lastcolor, count)
  return (data, wid, hei)

def generateFrame(filename, im, start_time, end_time, counter, sizelimit):
  data, ods_width, ods_height = toSubData(im, COLORS, sizelimit)

  # PCS - HEADER ==============================
  pcs = bytes([])
  pcs += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  pcs += numberToHexBytes(start_time, 4)
  #4 decoding time, always 0
  pcs += b'\x00\x00\x00\x00'
  #1 segment type
  pcs += PG_SEGMENT_TYPE['PCS']
  #2 segment size
  pcs += b'\x00\x13' #19

  # PCS - CONTENT

  #2 video width
  pcs += numberToHexBytes(sizelimit[0], 2)
  #2 video height
  pcs += numberToHexBytes(sizelimit[1], 2)
  #1 framerate
  pcs += b'\x10'
  #2 composition number
  pcs += numberToHexBytes(counter, 2)

  #1 types of composition
  # pcs += b'\x00' # normal - delete previous block
  # pcs += b'\x40' # acquisition point - refresh
  pcs += b'\x80' # epoch start - new block

  #1 palette update flag
  pcs += b'\x00' # True
  #pcs += b'\x80' # False

  #1 palette ID
  pcs += b'\x00'
  #1 composition object number
  pcs += b'\x01'
  #2 object ID
  pcs += b'\x00\x00'
  #1 window ID
  pcs += b'\x00'

  #1 cropped
  # pcs += b'\x40' # cropped
  pcs += b'\x00' # non-cropped

  #2 X offset in pixel
  pcs += numberToHexBytes(round(sizelimit[0]/2 - ods_width/2), 2)
  #2 Y offset in pixel
  pcs += numberToHexBytes(round(sizelimit[1] - ods_height - 10), 2)

  #2 X cropped offset - only if cropped = 0x40
  # pcs += b'\x00\x00'
  #2 Y cropped offset - only if cropped = 0x40
  # pcs += b'\x00\x00'
  #2 width cropped - only if cropped = 0x40
  # pcs += b'\x00\x00'
  #2 height cropped - only if cropped = 0x40
  # pcs += b'\x00\x00'

  # WDS - HEADER ==============================
  wds = bytes([])
  wds_window_number = 0
  wds += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  wds += numberToHexBytes(start_time, 4)
  #4 decoding time, always 0
  wds += b'\x00\x00\x00\x00'
  #1 segment type
  wds += PG_SEGMENT_TYPE['WDS']
  #2 segment size
  wds += b'\x00\x0a' #10

  # WDS - CONTENT
  #1 number of windows defined
  wds += numberToHexBytes(1, 1)
  #1 window ID
  wds += numberToHexBytes(0, 1)
  # NOTE same as PCS
  #2 window x offset (hor)
  wds += numberToHexBytes(round(sizelimit[0]/2 - ods_width/2), 2)
  #2 window y offset (vert)
  wds += numberToHexBytes(round(sizelimit[1] - ods_height - 10), 2)
  #2 width
  wds += numberToHexBytes(ods_width, 2)
  #2 height
  wds += numberToHexBytes(ods_height, 2)

  # PDS - HEADER ==============================
  pds = bytes([])
  color_counter = 0
  pds += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  pds += numberToHexBytes(start_time, 4)
  #4 decoding time, always 0
  pds += b'\x00\x00\x00\x00'
  #1 segment type
  pds += PG_SEGMENT_TYPE['PDS']
  #2 segment size
  pds += numberToHexBytes(2 + 5 * len(COLORS), 2)

  # PDS - CONTENT

  #1 palette ID
  pds += b'\x00'
  #1 palette version number
  pds += b'\x00'

  # describe each color in palette
  for color in COLORS:
    pds += numberToHexBytes(color_counter, 1) + color
    color_counter += 1

  # ODS - CONTENT ==============================
  ods_content = bytes([])

  #2 object ID
  ods_content += b'\x00\x00'
  #1 object version number
  ods_content += b'\x00'

  #1 sequence
    # ods_content += b'\x40' # last in sequence
    # ods_content += b'\x80' # first in sequence
  ods_content += b'\xC0' # first and last in sequence

  #3 data lenght
  # NOTE +4, discovered by studying real PGS
  ods_content += numberToHexBytes(len(data) + 4, 3)

  #2 width of image
  ods_content += numberToHexBytes(ods_width, 2)
  #2 height of image
  ods_content += numberToHexBytes(ods_height, 2)

  # data
  ods_content += data

  # ODS - HEADER
  ods = bytes([])
  ods += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  ods += numberToHexBytes(start_time, 4)
  #4 decoding time, always 0
  ods += b'\x00\x00\x00\x00'
  #1 segment type
  ods += PG_SEGMENT_TYPE['ODS']
  #2 segment size
  # NOTE +11, discovered by studying real PGS
  ods += numberToHexBytes(len(data) + 11, 2)

  ods = ods + ods_content

  # END - HEADER ==============================
  end = bytes([])
  end += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  end += numberToHexBytes(start_time, 4)
  #4 decoding time, always 0
  end += b'\x00\x00\x00\x00'
  #1 segment type
  end += PG_SEGMENT_TYPE['END']
  #2 segment size
  end += b'\x00\x00'

  sub = pcs + wds + pds + ods + end

  # endPCS - HEADER ==============================
  counter += 1
  pcs = bytes([])
  pcs += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  pcs += numberToHexBytes(end_time, 4)
  #4 decoding time, always 0
  pcs += b'\x00\x00\x00\x00'
  #1 segment type
  pcs += PG_SEGMENT_TYPE['PCS']
  #2 segment size
  pcs += b'\x00\x0b' #11

  # endPCS - CONTENT

  #2 video width
  pcs += numberToHexBytes(sizelimit[0], 2)
  #2 video height
  pcs += numberToHexBytes(sizelimit[1], 2)
  #1 framerate
  pcs += b'\x10'
  #2 composition number
  pcs += numberToHexBytes(counter, 2)

  #1 types of composition
  pcs += b'\x00' # normal - delete previous block
  # pcs += b'\x40' # acquisition point - refresh
  # pcs += b'\x80' # epoch start - new block

  #1 palette update flag (palette only update?)
  pcs += b'\x00' # True
  #pcs += b'\x80' # False

  #1 palette ID
  pcs += b'\x00'
  #1 composition object number (count)
  pcs += b'\x00'

  # endWDS - HEADER ==============================
  wds = bytes([])
  wds_window_number = 0
  wds += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  wds += numberToHexBytes(end_time, 4)
  #4 decoding time, always 0
  wds += b'\x00\x00\x00\x00'
  #1 segment type
  wds += PG_SEGMENT_TYPE['WDS']
  #2 segment size
  wds += b'\x00\x0a' #10

  # endWDS - CONTENT
  #1 number of windows defined
  wds += numberToHexBytes(1, 1)
  #1 window ID
  wds += numberToHexBytes(0, 1)
  # NOTE same values as PCS
  #2 window x offset (hor)
  wds += numberToHexBytes(round(sizelimit[0]/2 - ods_width/2), 2)
  #2 window y offset (vert)
  wds += numberToHexBytes(round(sizelimit[1] - ods_height - 10), 2)
  #2 width
  wds += numberToHexBytes(ods_width, 2)
  #2 height
  wds += numberToHexBytes(ods_height, 2)

  # endEND - HEADER ==============================
  end = bytes([])
  end += PG_ESCAPE #2

  #4 start time = seconds * 1000 (ms) * 90 (hz) 
  end += b'\x00\x00\x00\x00'
  #4 decoding time, always 0
  end += b'\x00\x00\x00\x00'
  #1 segment type
  end += PG_SEGMENT_TYPE['END']
  #2 segment size
  end += b'\x00\x00'

  sub = sub + pcs + wds + end
  return sub