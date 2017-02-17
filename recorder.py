# Part of the code has been updated from
# http://www.swharden.com/wp/2013-05-09-realtime-fft-audio-visualization-with-python/
# Author: Scott W Harden: neuroscientist, dentist, molecular biologist, code monkey (2013)

import matplotlib
matplotlib.use('TkAgg') # <-- THIS MAKES IT FAST!
import numpy
import scipy
import struct
import pyaudio
import threading
import pylab
import struct


class SwhRecorder:
    """Simple, cross-platform class to record from the microphone."""
    
    def __init__(self):
        """minimal garb is executed when class is loaded."""
        self.BUFFERSIZE=2**13 #1024 is a good buffer size
        self.secToRecord=.1
        self.threadsDieNow=False
        self.newAudio=False
        # Set sampling rate (in Hz).
        # Typical rates: {8000, 11025, 22050, 44100, 48100} Hz
        self.RATE = 44100;
        # Choose response type.
        # Note: {'fast' = ~125 ms, 'slow' = ~1.0 s}
        self.responseType = 'fast';
        # Set calibration constant.
        # Note: A quite location will be ~55 dBA.
        self.C = 50;
        
    def setup(self):
        """initialize sound card."""
        #TODO - windows detection vs. alsa or something for linux
        #TODO - try/except for sound card selection/initiation

        if self.responseType=='slow':
            self.secToRecord=1.0
        else:
            self.secToRecord= 0.125

        self.buffersToRecord=int(self.RATE*self.secToRecord/self.BUFFERSIZE)
        if self.buffersToRecord==0: self.buffersToRecord=1
        self.samplesToRecord=int(self.BUFFERSIZE*self.buffersToRecord)
        self.chunksToRecord=int(self.samplesToRecord/self.BUFFERSIZE)
        self.secPerPoint=1.0/self.RATE
        
        self.p = pyaudio.PyAudio()
        self.inStream = self.p.open(format=pyaudio.paFloat32,channels=1,rate=self.RATE,input=True,frames_per_buffer=self.BUFFERSIZE)
        
        self.xsBuffer=numpy.arange(self.BUFFERSIZE)*self.secPerPoint
        self.xs=numpy.arange(self.chunksToRecord*self.BUFFERSIZE)*self.secPerPoint
        self.audio=numpy.empty((self.chunksToRecord*self.BUFFERSIZE),dtype=numpy.float32)               
    
    def close(self):
        """cleanly back out and release sound card."""
        self.p.close(self.inStream)
    
    ### RECORDING AUDIO ###  
    
    def getAudio(self):
        """get a single buffer size worth of audio."""
        audioString=self.inStream.read(self.BUFFERSIZE)
        return numpy.fromstring(audioString,dtype=numpy.float32)
        
    def record(self,forever=True):
        """record secToRecord seconds of audio."""
        while True:
            if self.threadsDieNow: break
            for i in range(self.chunksToRecord):
                self.audio[i*self.BUFFERSIZE:(i+1)*self.BUFFERSIZE]=self.getAudio()
            self.newAudio=True 
            if forever==False: break

    def getRecord(self):
        """record secToRecord seconds of audio."""
        for i in range(self.chunksToRecord):
            self.audio[i*self.BUFFERSIZE:(i+1)*self.BUFFERSIZE]=self.getAudio()
            rec=self.audio
        return rec
    
    def continuousStart(self):
        """CALL THIS to start running forever."""
        self.t = threading.Thread(target=self.record)
        self.t.start()
        
    def continuousEnd(self):
        """shut down continuous recording."""
        self.threadsDieNow=True

    ### MATH ###
            
    def downsample(self,data,mult):
        """Given 1D data, return the binned average."""
        overhang=len(data)%mult
        if overhang: data=data[:-overhang]
        data=numpy.reshape(data,(len(data)/mult,mult))
        data=numpy.average(data,1)
        return data    
        
    def fft(self,data=None):
        if data==None: 
            data=self.audio.flatten()
        left,right=numpy.split(numpy.abs(numpy.fft.fft(data)),2)
        ys=numpy.add(left,right[::-1])
        # Determine FFT frequencies.
        xs = (1.*self.RATE/len(ys))*numpy.arange(0,len(ys))
        return xs,ys

    def level(self,data=None):
        if data==None: 
            data=self.audio.flatten()
        # Calculate magnitude of FFT.
        X = numpy.abs(numpy.fft.fft(data))
        # Add offset to prevent taking the log of zero.
        X[X == 0] = 1e-17
        # Retain frequencies below Nyquist rate.
        f = (1.*self.RATE/len(X))*numpy.arange(0,len(X))
        ind = f<self.RATE/2.; f = f[ind]; X = X[ind]
        # Apply A-weighting filter.
        A = self.filterA(f)
        X = A*X
        # Estimate dBA value using Parseval's relation.
        totalEnergy = numpy.sum(X**2)/len(X)
        meanEnergy = totalEnergy/((1./self.RATE)*len(X))
        dBA = 10.*numpy.log10(meanEnergy)+self.C
        # Estimate decibel level (for visualization).
        X = 20.*numpy.log10(numpy.abs(X))
        return f, X, dBA

    def filterA(self,f):
        # FILTERA Generates an A-weighting filter.
        #    FILTERA Uses a closed-form expression to generate
        #    an A-weighting filter for arbitary frequencies.
        #
        # Author: Douglas R. Lanman, 11/21/05
        # Define filter coefficients.
        # See: http://www.beis.de/Elektronik/AudioMeasure/
        # WeightingFilters.html#A-Weighting
        c1 = 3.5041384e16
        c2 = 20.598997**2
        c3 = 107.65265**2
        c4 = 737.86223**2
        c5 = 12194.217**2
        # Evaluate A-weighting filter.
        f[f == 0] = 1e-17;
        f = f**2
        num = c1*f**4
        den = ((c2+f)**2)*(c3+f)*(c4+f)*((c5+f)**2)       
        A = num/den
        return A
    
    ### VISUALIZATION ###
    
    def plotAudio(self):
        """open a matplotlib popup window showing audio data."""
        pylab.plot(self.audio.flatten())
        pylab.show()        
            
