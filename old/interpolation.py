from __future__ import print_function
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt
import tqdm
from scipy.interpolate import interp1d

pathfile = "/media/filippo/label/Codes/Github/EagleLogTools/Logs/test_parcheggio/collections_exportate_csv/eagle_test/20200223_185312_Nicola_Autocross/"
filename = "imu_accel.csv"

log = open(pathfile + filename, "r")
lines = log.readlines()[1:]
dt = 0
x_ = []
y_ = []
z_ = []
scale = 0
prevdt = 0
currdt = 0
for line in lines:

    currdt = float(line.split("\t")[0])
    if (lines.index(line) != 0):
        dt += currdt - prevdt

    x_.append(float(line.split("\t")[1]))
    y_.append(float(line.split("\t")[2]))
    z_.append(float(line.split("\t")[3]))
    scale = int(line.split("\t")[4])

    prevdt = currdt
dt = dt/(len(lines)-1)

if len(x_) == len(y_) == len(z_):
    nsample = len(x_)
else:
    print("ERROR ON FILE LEN")


print("Found {} records with mean dt of {}. Total: {} seconds".format(
    nsample, dt, nsample*dt/1000))

y = x_

x = np.linspace(0.0, nsample*dt, nsample, endpoint=True)
f = interp1d(x, y, kind="cubic")
xnew = np.linspace(0, nsample*dt, num=nsample*20, endpoint=True)
plt.plot(x, y, '.', xnew, f(xnew), "-")
plt.legend(['data', 'cubic'], loc='best')

plt.grid()
plt.show()

######################################################################################################
#########------------------------------------------------------------------------------------#########
#########-------------------------------------SAMPLECODE-------------------------------------#########
#########------------------------------------------------------------------------------------#########
######################################################################################################
exit()
# sample spacing
sampling = 1024
nsample = 500
dt = 1.0 / sampling
x = np.linspace(0.0, nsample*dt, nsample, endpoint=True)
nu = 50.0  # frequency in Hz of the sine function
y = np.sin(nu * 2.0*np.pi*x)


f = interp1d(x, y, kind="cubic")
xnew = np.linspace(0, nsample*dt, num=nsample*20, endpoint=True)


plt.plot(x, y, '.', xnew, f(xnew), "-")
plt.legend(['data', 'cubic'], loc='best')

plt.grid()
plt.show()
######################################################################################################
#########------------------------------------------------------------------------------------#########
#########-------------------------------------SAMPLECODE-------------------------------------#########
#########------------------------------------------------------------------------------------#########
######################################################################################################
