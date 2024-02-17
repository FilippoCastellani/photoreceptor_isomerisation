import pickle
import numpy as np
from numpy import diff
import matplotlib.pyplot as plt

def plot_spectrum(LEDs, x, color_settings, plot_total=True, ylim=None):

    violet = color_settings[0]
    blue   = color_settings[1]
    green = color_settings[2]
    yellow = color_settings[3]
    red    = color_settings[4]

    fig , ax = plt.subplots(figsize=(5, 3))

    legend = []

    alpha = 0.3

    if violet>0:
        ax.plot(x,LEDs[0]*violet,   'violet')
        legend.append('385 nm')
    
    if blue>0:
        ax.plot(x,LEDs[1]*blue,     'blue', alpha = alpha)
        legend.append('415 nm')

    if green>0:
        ax.plot(x,LEDs[2]*green,    'green', alpha = alpha)
        legend.append('490 nm')
    
    if yellow>0:
        ax.plot(x,LEDs[3]*yellow,   'yellow')
        legend.append('530 nm')
    
    if red>0:
        ax.plot(x,LEDs[4]*red,      'red', alpha = alpha)
        legend.append('625 nm')

    if plot_total:
        LEDs_total = LEDs[0]*violet+LEDs[1]*blue+LEDs[2]*green+LEDs[3]*yellow+LEDs[4]*red
        ax.plot(x,LEDs_total, 'black', linewidth=0.8, alpha=0.5, linestyle= (0, (5, 5, 1, 3)))
        legend.append('Total')

    ax.fill_between(x,0,LEDs[0]*violet,alpha=0.1, color='violet')
    ax.fill_between(x,0,LEDs[1]*blue,alpha=0.1, color='blue')
    ax.fill_between(x,0,LEDs[2]*green,alpha=0.1, color='green')
    ax.fill_between(x,0,LEDs[3]*yellow,alpha=0.1, color='yellow')
    ax.fill_between(x,0,LEDs[4]*red,alpha=0.1, color='red')


    ax.legend(legend, bbox_to_anchor=(1.3, 0.8))

    if ylim is not None:
        ax.set_ylim(ylim)
    ax.set_xlabel('Lambda (nm)')
    ax.set_ylabel('Power (µW/cm²)')

    plt.show()
    plt.close()

def load_obj(name ):
    if name[-4:]=='.pkl':
        name = name[:-4]
    #~ try:
        #~ return pk5.dumps(name+'pkl', protocol=5)
    #~ except:
    with open( name + '.pkl', 'rb') as f:
        return pickle.load(f)

def save_obj(obj, name ):
    if name[-4:]=='.pkl':
        name = name[:-4]
    with open( name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def IlluminanceFactor(Amp1,AmpPhoto,wl):
    """""
    This function calculates the Illuminance Factor Product for a given LED source and a given target opsin.
    The Illuminance Factor Product is the product of the LED source amplitude, the target opsin spectra and the wavelength axis.

    Output is in isomerizations / s
    To get the result in photons/cm^2/s we have to multiply by 10^8 and divide by ac (x5 or x2 for rods)
    
    Parameters
    ----------
    Amp1 : numpy array
        The light (LED source) amplitude not normalized in µW/cm²
    AmpPhoto : numpy array
        The spectra of the target opsin normalized to 1 at the peak (a.u.)
    wl : numpy array
        The wavelength axis (nm)
    
    Returns
    -------
    IlluminanceFactor : numpy array
        The isomerizations / s

    Factors have units of:
    ----------------------
    ac = µm²
    hc = J.m
    10**23 puts all in µW - µm² 
    """""
    #Illuminance Factor Product hyperparameters
    h=6.63*10**(-34)                    # Planck constant J.s
    c=299792458                         # speed of light [m/s]  
    
    ac=[0.2,0.2,0.5,0.2,0.2]            # in µm²                                                                                    
    # ac_cones=0.2
    # ac_mela=0.2
    # ac_rods=0.5
    # ac_reach=0.2
    # ac_red=0.2

    IlluminanceFactor=[]
    for photo in range(len(AmpPhoto)):
        IlFa=0
        for I_wl in range(len(Amp1)):
            # Results in photoisomerisation/s /µm²
            IlFa+= Amp1[I_wl] * AmpPhoto[photo][I_wl] * wl[I_wl] * diff(wl)[10]  * ac[photo]/(h*c) *10**(-23)                                          # 10th element of diff is selected for experimental reasons
                    #µW/cm²   x   a.u.(peak at 1)    x nm (lambda) x lambda step x ph.µm² x 1/(Jm)  x convert to same units
        IlluminanceFactor.append(IlFa) 
    return np.array(IlluminanceFactor) #

def Write_fancy(result,F):
    o_names = ['Scones    ','Melanopsin','Rhodopsin ','Mcones    ','Red_opsin ']
    for i,r in enumerate(result):
        if F=='scientific':
            print(o_names[i],' :',"{:.2e}".format(r))
        else:
             print(o_names[i],' :',"{:10.0f}".format(r))

# Function that returns a voltage given a certain power value in percentage of max possible value  
def find_V(value,color, newVcurves,Vnew):

    Rmax = np.nanmax(newVcurves[0])
    Ymax = np.nanmax(newVcurves[1])
    Gmax = np.nanmax(newVcurves[2])
    Bmax = np.nanmax(newVcurves[3])
    Vmax = np.nanmax(newVcurves[4])
    
    if color =='r':
            array = newVcurves[0]
            vmax=Rmax
    elif color== 'y':
            array = newVcurves[1]
            vmax=Ymax
    elif color== 'g':
            array = newVcurves[2]
            vmax=Gmax
    elif color== 'b':
            array = newVcurves[3]
            vmax=Bmax
    elif color== 'v':
            array = newVcurves[4]
            vmax=Vmax
    
    array = np.asarray(array)
    idx = (np.abs(array - value*vmax)).argmin()

    print('The index is:',idx)

    return Vnew[idx]

def find_value(voltage,color,newVcurves,Vnew):

    Colormax = np.nanmax(newVcurves[color])

    array = newVcurves[color]
    array = np.asarray(array)
    idx = (np.abs(Vnew - voltage)).argmin()
    result = array[idx]/Colormax

    print('The index is:',idx)
    print('The desired voltage is:',voltage)
    print('The voltage found is:',Vnew[idx])
    print('The result is:',result)


    return result

#==============