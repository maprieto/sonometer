# -*- coding: utf-8 -*-
"""
Interface gráfica para un sonómetro dixital
@author: Andrés Prieto
"""

import numpy as np
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import wx
from recorder import *

# Time gap between uptades
REDRAW_TIMER_MS = 20

class App(wx.App):
    def OnInit(self):
        # Create main window
        self.paused=False
        self.frame=wx.Frame(None,-1,title='Sonómetro',size=(1000,710))
        self.frame.Show(True)
        # Create a sound recorder object
        self.SR=SwhRecorder()
        self.SR.setup()
        # Get data
        xt=self.SR.getRecord();
        # Compute dBA levels and FFT spectrum
        xs,ys,dBA=self.SR.level()
        # Create figure
        #col=self.frame.GetBackgroundColour().asTuple()
        figure = Figure(figsize=(10,6.8), dpi=100)
        #figure.set_facecolor((self.col[0]/255.,self.col[1]/255.,self.col[2]/255.))
        # Plot for the FFT spectrum
        ax_fft = figure.add_subplot(2,1,1)
        self.line_fft, =ax_fft.semilogx(xs, ys, 'b-',linewidth=1.0)
        ax_fft.set_xlabel('Frecuencia (Hz)'); ax_fft.xaxis.set_label_coords(0.7, -0.05)
        ax_fft.set_ylabel('Magnitude (dB)')
        ax_fft.set_title('Ponderacion-A da magnitude do espectro en frecuencias');
        ax_fft.set_xlim(100,1000); ax_fft.set_ylim(-100,60);
        xticks=np.append(np.linspace(100,1000,10),np.linspace(2000,10000,9))
        ax_fft.set_xticks(xticks)
        ax_fft.grid(True)
        # Plot for the time signal
        ax_signal = figure.add_subplot(2,2,3)
        xt=xt/np.linalg.norm(xt,np.inf)
        tt=np.linspace(0.,self.SR.secToRecord,xt.size)
        self.line_signal, =ax_signal.plot(tt, xt, 'b-',linewidth=1.0)
        ax_signal.set_xlabel('Tempo (s)')
        ax_signal.set_ylabel('Voltaxe normalizada')
        #ax_signal.set_title('Datos de entrada')
        ax_signal.grid(True)
        ax_signal.axis([tt[0],tt[-1],-1.,1.])
        # Print dB value
        axes_dB = figure.add_subplot(2,2,4)
        axes_dB.axis('off')
        self.textdB=axes_dB.text(1.0,0.5,"%5.2f dBA"%dBA, fontsize=38, horizontalalignment='right');
        self.canvas = FigureCanvas(self.frame, -1, figure)
        # Bottoms
        self.butclose=wx.Button(self.frame, -1, 'Close',pos=(900,680))
        self.butclose.Bind(wx.EVT_BUTTON, self.OnClose, self.butclose)
        #self.butstop=wx.Button(self.frame, -1, 'Stop',pos=(800,670))
        #self.Bind(wx.EVT_BUTTON, self.OnStop, self.butstop)
        self.pause_button = wx.Button(self.frame, -1, "Pause", pos=(800,680))
        self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.pause_button.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        # Define timer
        self.redraw_timer = wx.Timer(self.frame)
        self.Bind(wx.EVT_TIMER, self.update_plot, self.redraw_timer)        
        self.redraw_timer.Start(REDRAW_TIMER_MS)
        # Fit size to elements
        #frame.Fit()
        return True

    def on_pause_button(self, event):
        self.paused = not self.paused

    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)
    
    def update_plot(self, event):
        if not self.paused:
            # Get data
            xt=self.SR.getRecord();
            # update plots FFT and signal
            xs,ys,dBA=self.SR.level()
            xt=xt/np.linalg.norm(xt,np.inf)
            self.line_signal.set_ydata(xt)
            self.line_fft.set_ydata(ys)
            self.textdB.set_text("%5.2f dBA"%dBA)
            self.canvas.draw()
    
    def OnClose(self,event):
        self.frame.Destroy()
    
    #def OnStop(self,event):
    #    if not self.paused:
    #        self.paused==True
    #        self.butstop.SetLabel('Start')
    #    else:
    #        self.paused=False
    #        self.butstop.SetLabel('Stop')

app=App()
app.MainLoop()

