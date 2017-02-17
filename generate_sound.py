import math
import pyaudio
import sys

PyAudio = pyaudio.PyAudio


def playTone(rate,wave,time,channel):
  data = ''.join([chr(int(math.sin(x/((rate/wave)/math.pi))*127+128)) for x in xrange(rate)])
  p = PyAudio()

  stream = p.open(format =
    p.get_format_from_width(1),
    channels = channel,
    rate = rate,
    output = True)
  for DISCARD in xrange(int(time)):
      stream.write(data)
  #stream.stop_stream()
  #stream.close()
  #p.terminate()


'''
import generate_sound
# https://www.youtube.com/watch?v=33qV3d3U0q4
generate_sound.playTone(88000,400,1,2)

#https://www.youtube.com/watch?v=4yL75EvCp0w
generate_sound.playTone(88000,800,1,2)
'''

def scale(noteNumber):
  counter = 100
  while noteNumber*100 > counter:
    playTone(88000,100+counter,1,2)
    counter += 100

#scale(10)
