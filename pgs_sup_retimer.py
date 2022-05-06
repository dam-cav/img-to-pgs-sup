import argparse

parser = argparse.ArgumentParser(description='PGS SUP file subtitle timing bulk changer.')

parser.add_argument("-i",  "--input",    help="sup input path",                         default=None)
parser.add_argument("-o",  "--output",   help="sup output path",                        default=None)
parser.add_argument("-s",  "--sum",      help="sum given milliseconds (even negative)", default="0")
parser.add_argument("-m",  "--multiply", help="mupltiply times for given value",        default="1")
ARGS = parser.parse_args()

PGS_DELIMITER = b'\x50\x47'
FREQUENCE = 90
# PG_SEGMENT_TYPE = {
#   16: 'PCS',
#   17: 'WDS',
#   14: 'PDS',
#   15: 'ODS',
#   80: 'END',
# }

infile = open(ARGS.input,"rb")
infile = infile.read()

pgs_blocks = infile.split(PGS_DELIMITER)

print('Recalculating times...')
for index, block in enumerate(pgs_blocks):
  #segment_type = block[8:9]
  current_time = int.from_bytes(block[:4], 'big')

  current_time += int(ARGS.sum) * 90
  current_time *= float(ARGS.multiply)
  
  #clamp time
  current_time = max(0, min(current_time, 4294967295))

  new_time = round(current_time).to_bytes(4, 'big')
  pgs_blocks[index] = new_time + block[4:]

result = PGS_DELIMITER + PGS_DELIMITER.join(pgs_blocks[1:])

outfile = open(ARGS.output,"wb")
outfile.write(result)
outfile.close()
print('DONE')