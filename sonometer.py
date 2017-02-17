# Sonometer using pyaudio and matplotlib
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from recorder import *

# Setup for latex amsmath
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}\usepackage[utf8]{inputenc}"]
matplotlib.rcParams.update({'font.size': 20,'legend.labelspacing':0.1})

# Create a sound recorder object
SR=SwhRecorder()
SR.setup()
SR.continuousStart()

# Turn interactive mode on
plt.ion()

# Get data
xt=SR.audio;

# First FFT plot
xs,ys,dBA=SR.level()
fig_fft=plt.figure()
ax_fft=plt.gca()
line_fft, =ax_fft.semilogx(xs, ys, 'b-',linewidth=2.0)
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('Magnitude (dB)')
plt.title('Ponderacion-A da magnitude do espectro en frecuencias');
plt.xlim(100,1000); plt.ylim(-100,60);
xticks=numpy.append(numpy.linspace(100,1000,10),numpy.linspace(2000,10000,9))
plt.xticks(xticks)
plt.grid(True)
#plt.axis('tight')

# First signal plot
xt=xt/np.linalg.norm(xt,np.inf)
tt=np.linspace(0.,SR.secToRecord,xt.size)
fig_signal=plt.figure()
ax_signal=plt.gca()
line_signal, =ax_signal.plot(tt, xt, 'b-',linewidth=2.0)
plt.xlabel('Tempo (s)')
plt.ylabel('Voltaxe normalizada')
plt.title('Datos de entrada')
plt.grid(True)
plt.axis([tt[0],tt[-1],-1.,1.])

# Show both plots
plt.show()

# Update plots for signal and FFT values
while SR.newAudio==True:
    # Get audio data
    xt=SR.audio; 
    # Plot FFT
    xs,ys,dBA=SR.level()
    line_fft.set_ydata(ys)
    fig_fft.canvas.draw()
    # Plot signal
    xt=xt/np.linalg.norm(xt,np.inf)
    line_signal.set_ydata(xt)
    fig_signal.canvas.draw()

