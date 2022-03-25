# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import Frame, Label, Entry, messagebox, Checkbutton, IntVar, StringVar, Menu, filedialog
from typing import List
from scipy.io import wavfile
import numpy as np
import os

from PIL import ImageTk, Image
from matplotlib.figure import Figure
from tx_frame import TxFrame
from tx_model import TxModel
from rx_model import RxModel
import re
from numpy import pi, cos, sin
from rss_utils import get_random_color
import sys
import matplotlib
matplotlib.use('TkAgg')
from mpl_toolkits.mplot3d import Axes3D, art3d
import matplotlib.pyplot as plt
from signallib import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


"""
    Regular Expression for a number, including Integer, float, 
    and scientific notation number like 1.8e9
"""
_NUMBER__REG = re.compile(r'^[+-]?\d+(\.\d+)?([eE][-+]?\d+)?$')
# _NUMBER__REG = re.compile(r'^-?\d+\.?\d*$')


"""
    String is a number or not?
    String is user's input.
"""
def is_number(string):
    condition = _NUMBER__REG.search(string)
    if condition:
        return True
    return False


"""
    The main Class use Tkinter's GUI
"""
class Root(Tk):

    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.dest)
        self.d_view_draw = False
        self.have_result = False

        self.init_all()

    def dest(self):
        self.destroy()
        os._exit(1)
        sys.exit()

    def init_all(self):
        self.title('RSS ---- by Wenxiao WANG')
        self.algo = 0
        self.init_tx_model()
        self.init_frame()
        self.init_settings_interface()

    """
        Default settings for LEDs.
        We can use maxmum 9 LEDs for the positionning. Default we use 3 of them.
        If we let 'status=False', we will not use this LED.
    """
    def init_tx_model(self):
        self.__t1 = TxModel(0, x=-0.5, y=0.6, z=2.195, pr=3354, pt=20886, m=1.5684159304466327)
        self.__t2 = TxModel(1, x=0, y=-1.5, z=3, status=False)
        self.__t3 = TxModel(2, x=1.5, y=1.5, z=3, pr=3354, status=False)
        self.__t4 = TxModel(3, x=-1.5, y=0, z=3, status=False)
        self.__t5 = TxModel(4, x=0, y=0, z=3, status=False)
        self.__t6 = TxModel(5, x=1.5, y=0, z=3, status=False)
        self.__t7 = TxModel(6, x=-0.5, y=0.25, z=2.195, pr=3354, pt=20886, m=1.5684159304466327)
        self.__t8 = TxModel(7, x=0, y=1.5, z=3, status=False)
        self.__t9 = TxModel(8, x=0.5, y=0.25, z=2.195, pr=3354, pt=20886, m=1.5684159304466327)
        self.__tx_list = [
            self.__t1,
            self.__t2,
            self.__t3,
            self.__t4,
            self.__t5,
            self.__t6,
            self.__t7,
            self.__t8,
            self.__t9]

    """
        Initialise all Frames for the GUI.
    """
    def init_frame(self):
        self.menubar = Menu(self)

        self.__modeling_3d_frame = Frame(
            self, bd=1, relief=GROOVE, padx=8, pady=5)
        self.__modeling_3d_frame.pack(side='right')

        self.set_canvas(status=False)

        self.__left_frame = Frame(self, bd=1, relief=GROOVE, padx=8, pady=5)
        self.__left_frame.pack(side='left')

        self.__logo_frame = Frame(self.__left_frame, bd=1, relief=GROOVE, padx=8, pady=5)
        self.__logo_frame.pack(side='top')

#         self.set_logo()
#  no logo

        self.__tx_settings_frame = TxFrame(self.__left_frame, self.__tx_list)
        self.__tx_settings_frame.pack()

        self.__bot_frame = Frame(self.__left_frame, bd=1, relief=GROOVE, padx=5, pady=5)
        self.__bot_frame.pack(side='bottom')

        self.__algo_settings_frame = Frame(self.__bot_frame, bd=1, relief=GROOVE, padx=5, pady=5)
        self.__algo_settings_frame.pack(side='right')

        self.__r_settings_frame = Frame(self.__bot_frame, bd=1, relief=GROOVE, padx=5, pady=5)
        self.__r_settings_frame.pack(side='left')

    """
        Set ISEP logo, IORL logo and 5GPPP logo.
   """
    def set_logo(self):
        script_dir = os.path.dirname(__file__)

        img = Image.open(os.path.join(script_dir, "icon/iorl-logo-300x85.jpg"))
        img = img.resize((120,40), Image.ANTIALIAS)
        self.iorl = ImageTk.PhotoImage(img)
        self.iorl_panel = Label(self.__logo_frame, image=self.iorl)
        self.iorl_panel.pack(side=LEFT)
        img = Image.open(os.path.join(script_dir, "icon/Logo_isep_300x175.jpg"))
        img = img.resize((120,40), Image.ANTIALIAS)
        self.isep = ImageTk.PhotoImage(img)
        self.isep_panel = Label(self.__logo_frame, image=self.isep)
        self.isep_panel.pack(side=LEFT)
        img = Image.open(os.path.join(script_dir, "icon/new-5g-header-1.png"))
        img = img.resize((120,40), Image.ANTIALIAS)
        self.new5g = ImageTk.PhotoImage(img)
        self.new5g_panel = Label(self.__logo_frame, image=self.new5g)
        self.new5g_panel.pack(side=LEFT)

    """
        Check is the Checkbutton for the Detail mode seleted.
        if yes, show the detail mode if the calculation haven't problem.
        if not, hide detail mode
    """
    def d_view_change(self):
        if self.__d_view_status.get() == 1:
            self.d_view_draw = True
            if self.have_result:
                self.distance_error.set(
                    "Error between real distance and estimated distance\n")
                self.set_canvas([self.r.x], [self.r.y], # self.r is the variable save the PD receiver
                                [self.r.z], d_view=True)
        else:
            self.d_view_draw = False
            if self.have_result:
                self.distance_error.set("")
                self.set_canvas([self.r.x], [self.r.y], [self.r.z])

    """
        Set Canvas Frame, this frame display the 3D model of the positionning.

    """
    def set_canvas(
            self,
            x2=[],
            y2=[],
            z2=[],
            rx=1,
            ry=1,
            status=True,
            d_view=False):
        if status:
            self.fig.clear()
        else:
            self.fig = plt.figure(figsize=(5, 4), dpi=130)
            self.canvas = FigureCanvasTkAgg(
                self.fig, master=self.__modeling_3d_frame)
            self.canvas.get_tk_widget().pack(side='bottom', fill='both')

            toolbar = NavigationToolbar2Tk(self.canvas, self)
            toolbar.update()
            self.canvas._tkcanvas.pack(side='bottom', fill='both', expand=1)
        
        # The empty 3D axe
        ax = Axes3D(self.fig)

        # set top's area and bottom's area
        tmp = 1
        top = [(-tmp, 0, 2.195),
               (tmp, 0, 2.195),
               (tmp, 1, 2.195),
               (-tmp, 1, 2.195)]

        bot = [(-tmp, 0, 0),
               (tmp, 0, 0),
               (tmp, 1, 0),
               (-tmp, 1, 0)]

        # Alpha set the transparency
        bot_face = art3d.Poly3DCollection([bot], alpha=0.5, linewidths=1)
        top_face = art3d.Poly3DCollection([top], alpha=0.5, linewidths=1)

        alpha = 0.5
        bot_face.set_facecolor((0, 0, 1, alpha))
        top_face.set_facecolor((0, 0, 1, alpha))

        # Add two area to 3D axe
        ax.add_collection3d(bot_face)
        ax.add_collection3d(top_face)

        x = []
        y = []
        z = []
        ds = []

        n = 0
        # check if detail mode is on or off.
        if d_view:
            for it in self.r.get_txs(): # txs is the all LEDs used. Save each led's position and 
                x.append(it.get_x())    # distance to receiver.
                y.append(it.get_y())
                z.append(it.get_z())
                ds.append(self.r.get_ds()[n])
                n += 1
        else:
            for it in self.__tx_list: # if Not in detail mode, save only the position.
                if it.get_status():
                    x.append(it.get_x())
                    y.append(it.get_y())
                    z.append(it.get_z())

        if d_view: # draw the circle for each LED
            for it in range(len(x)):
                self.draw_d_circle(ax, plt, x[it], y[it], z[it], ds[it])
            string = self.distance_error.get()
            string += self.r.d_error
            self.distance_error.set(string)

        # scatter3D draw point in the 3D Axe.
        ax.scatter3D(x, y, z, c='red', marker='o')
        ax.scatter3D(x2, y2, z2, c='green', marker='o')
        if len(x2) != 0: # if we know the real position of receiver.
            pos = "Real Location: (%.3fm, %.3fm, %.3fm)" % (rx, ry, z2[0])
            ax.text2D(0.05, 0.95, pos, transform=ax.transAxes)
            ax.scatter3D([rx], [ry], [0], c='yellow', marker='o')

        ax.set_xlabel('x axis')
        ax.set_xlim(-tmp, tmp)
        ax.set_ylabel('y axis')
        ax.set_ylim(0, 1)
        ax.set_zlabel('z axis')
        ax.set_zlim(0, 2.195)
        self.canvas.draw()


    """
        Use that function for draw the circle for a Led.
    """
    def draw_d_circle(self, ax, plt, x, y, z, d):
        couleur = get_random_color()
        x1 = [i for i in self.line_list(x, x, 360)]
        y1 = [i for i in self.line_list(y, y, 360)]
        z1 = [i for i in self.line_list(z, 0, 360)]
        r2 = d**2 - z**2
        r = pow(r2, 1.0 / 2) # get the distance to receiver in the bottom area.
        angles_circle = [i * pi / 180 for i in range(0, 360)]
        x_list_circle = r * cos(angles_circle) + x
        y_list_circle = r * sin(angles_circle) + y
        ax.plot(x1, y1, z1, couleur, ls=":")
        plt.plot(x_list_circle, y_list_circle, couleur, alpha=0.5)
        plt.plot([x], [y], "o", c=couleur)

    """
        Use that to save the point for a line.
        a is the begin, e is the end, m is number of point.
    """
    def line_list(self, a, e, n):
        step = (e - a) / n
        res = list()
        tmp = a
        for it in range(n - 1):
            tmp += step
            res.append(tmp)
        res.append(e)
        return res

    """
        The 'Positioning' Button will run this function.
    """
    def get_result(self):
        if self.validate_input(): # Check user's input. If all input is legal.
            # get all input for create a receiver's class named RxModel.
            self.r = RxModel(float(self.x.get()),
                             float(self.y.get()),
                             float(self.z.get()),
                             float(self.apd_input.get()),
                             self.__tx_list,
                             self.algo)
            string = "Estimated location : x = %.3fm, y = %.3fm, z = 0m" % (self.r.x, self.r.y)
            # set 3D axes for display the result in 3D.
            self.set_canvas([self.r.x], [self.r.y], [0],
                            self.r.rx, self.r.ry, d_view=self.d_view_draw)
            self.result.set(string)
            error = np.sqrt((self.r.x - self.r.rx)**2 + (self.r.y - self.r.ry)**2)
            result_error_message = "Error: {}m".format(error)
            self.result_error.set(result_error_message)
            self.have_result = True

    def validate_input(self): # Check user's input. If all input is legal.
        if not is_number(self.apd_input.get()):
            messagebox.showinfo("Warning!", "APD input Error!")
            return False
        if not is_number(self.z.get()):
            messagebox.showinfo("Warning!", "Z input Error!")
            return False
        if not is_number(self.y.get()):
            messagebox.showinfo("Warning!", "Real Y input Error!")
            return False
        if not is_number(self.x.get()):
            messagebox.showinfo("Warning!", "Real X input Error!")
            return False
        return True

    # Use all LEDs who send the signal for positionning.
    def set_algo_all_tx(self):
        self.algo_string.set("All Tx algorithm")
        self.algo = 0

    # Use only 3 LEDs who send maximum signal.
    def set_algo_3_max_tx(self):
        self.algo_string.set("3 max Tx algorithm")
        self.algo = 3

    """
        Read the RSS file we saved, part of parameters can't change in GUI
        the default parameter is according the real enviroment of ISEP and 
        the datasheet of LED/receiver used.
    """
    def read_from_file(self):
        filename = filedialog.askopenfilename()
        Fe = float(self.pd_f.get()) # get the input for the receiver's frequency used.
        fftsize = 2 # Can't change in GUI, the parameter used for fft.

        # Not using in code. Because it's default value for the get_data_from_file.
        R_PD = 1.9E4 
        I_620 = 0.4
        D_PD = 3E-3 

        T = float(self.pd_t.get())
        T_begin = float(self.signal_begin.get())
        T_end = float(self.signal_end.get())
        N1s = float(self.N1sv.get())
        # The frequency range according to the 3 LEDs used in ISEP
        F_begin = [4.9e5, 6.9e5, 8.9e5] # 500000 Hw, 700000 Hw, 900000 Hz
        F_end = [5.1e5, 7.1e5, 9.1e5]

        # This function is defined in the file signallib.py
        # Get data in the file
        datas, llms, lm_mean = get_data_from_file(filename, T, T_begin, T_end, Fe, fftsize, N1s, F_begin, F_end, plotable=False)

        # Set the data to the GUI and give a result
        if self.validate_input():
            self.__tx_list[0].set_pr(lm_mean[1])
            self.__tx_settings_frame._TxFrame__tx_settings_frame[0].pr.set(self.__tx_list[0].get_pr())
            self.__tx_list[6].set_pr(lm_mean[0])
            self.__tx_settings_frame._TxFrame__tx_settings_frame[6].pr.set(self.__tx_list[6].get_pr())
            self.__tx_list[8].set_pr(lm_mean[2])
            self.__tx_settings_frame._TxFrame__tx_settings_frame[8].pr.set(self.__tx_list[8].get_pr())
            self.r = RxModel(float(self.x.get()),
                             float(self.y.get()),
                             float(self.z.get()),
                             float(self.apd_input.get()),
                             self.__tx_list,
                             self.algo)
            string = "Estimated location : x = %.3fm, y = %.3fm, z = 0m" % (self.r.x, self.r.y)
            self.set_canvas([self.r.x], [self.r.y], [0],
                            self.r.rx, self.r.ry, d_view=self.d_view_draw)
            self.result.set(string)
            error = np.sqrt((self.r.x - self.r.rx)**2 + (self.r.y - self.r.ry)**2)
            result_error_message = "Error: {}m".format(error)
            self.result_error.set(result_error_message)
            self.have_result = True

        print(lm_mean)

    # Read the file saved by USRP
    def pd_receive_signal(self):
        savefile = filedialog.asksaveasfilename()
        fe = float(self.pd_f.get())
        time = float(self.pd_t.get())*fe
        # This is a bash's command in the terminal
        commande = "python2 receveid_signal_script.py --filename='" + savefile + "' --samp-rate="+str(fe)+ " --time=" + str(time)
        os.system(commande)

    # new record from raspcode
    def pd_record_from_rasp(self):
        rate = self.pd_f.get()
        input_device_index = self.input_device_index.get()
        wave_output_filename = self.wave_output_filename.get()
        record_seconds = self.pd_t.get()
        # This is a bash's command in the terminal
        commande = "python3 ./raspcode/record.py " + rate + " " + input_device_index + \
            " " + wave_output_filename + " " + record_seconds
        os.system(commande)
        # Calculate Pr
        file_path = 'output.wav'
        sampling_rate, data_array = wavfile.read(wave_output_filename)
        data = data_array.tolist()
        DURATION = 10
        lenData = len(data)
        i = 0
        Powerdata = [0] * lenData
        while i < lenData:
            Powerdata[i] = data[i] * data[i]
            i = i + 1
        vav = sum(Powerdata) / lenData
        Pr1_Rasp = vav ** 0.5
        Pr2_Rasp = 3354
        Pr3_Rasp = 3354
        # estimate the location
        if self.validate_input():
            self.__tx_list[0].set_pr(Pr1_Rasp)
            self.__tx_settings_frame._TxFrame__tx_settings_frame[0].pr.set(self.__tx_list[0].get_pr())
            self.__tx_list[6].set_pr(Pr2_Rasp)
            self.__tx_settings_frame._TxFrame__tx_settings_frame[6].pr.set(self.__tx_list[6].get_pr())
            self.__tx_list[8].set_pr(Pr3_Rasp)
            self.__tx_settings_frame._TxFrame__tx_settings_frame[8].pr.set(self.__tx_list[8].get_pr())
            self.r = RxModel(float(self.x.get()),
                             float(self.y.get()),
                             float(self.z.get()),
                             float(self.apd_input.get()),
                             self.__tx_list,
                             self.algo)
            string = "Estimated location : x = %.3fm, y = %.3fm, z = 0m" % (self.r.x, self.r.y)
            self.set_canvas([self.r.x], [self.r.y], [0],
                            self.r.rx, self.r.ry, d_view=self.d_view_draw)
            self.result.set(string)
            error = np.sqrt((self.r.x - self.r.rx)**2 + (self.r.y - self.r.ry)**2)
            result_error_message = "Error: {}m".format(error)
            self.result_error.set(result_error_message)
            self.have_result = True


    # set the Button, Label, in the GUI
    def init_settings_interface(self):
        self.result = StringVar(self.__modeling_3d_frame,
                                "Estimated location: x = ?, y = ?, z = ?")
        self.result_label = Label(self.__modeling_3d_frame,
                                  textvariable=self.result)
        self.result_label.pack()

        self.result_error = StringVar(self.__modeling_3d_frame,
                                      "Error: ?")
        self.result_error_label = Label(self.__modeling_3d_frame,
                                        textvariable=self.result_error)
        self.result_error_label.pack()

        self.distance_error = StringVar(self.__modeling_3d_frame,
                                        "")
        self.distance_error_label = Label(self.__modeling_3d_frame,
                                          textvariable=self.distance_error)
        self.distance_error_label.pack()

        self.__r_settings_label = Label(self.__r_settings_frame,
                                        text="Settings for Rx")
        self.__r_settings_label.grid(row=0)

        self.algo_string = StringVar(
            self.__r_settings_frame,
            "3 max Tx algorithm")
        self.algo_label = Label(self.__r_settings_frame,
                                textvariable=self.algo_string)
        self.algo_label.grid(row=0, column=2)

        self.apd_label = Label(self.__r_settings_frame, text="APD  =")
        self.apd_label.grid(row=1, column=0, padx=5, pady=5)
        self.apd = StringVar(self.__r_settings_frame, "7.0686e-2")
        self.apd_input = Entry(self.__r_settings_frame,
                               textvariable=self.apd,
                               width=8)
        self.apd_input.grid(row=1, column=1, padx=5, pady=5)

        self.r_z_label = Label(self.__r_settings_frame, text="Z  =")
        self.r_z_label.grid(row=2, column=0, padx=5, pady=5)
        self.z = StringVar(self.__r_settings_frame, "0")
        self.r_z_input = Entry(self.__r_settings_frame,
                               textvariable=self.z,
                               width=4)
        self.r_z_input.grid(row=2, column=1, padx=5, pady=5)

        self.r_x_label = Label(self.__r_settings_frame, text="Real X =")
        self.r_x_label.grid(row=3, column=0, padx=10, pady=10)
        self.x = StringVar(self.__r_settings_frame, "0")
        self.r_x_input = Entry(self.__r_settings_frame,
                               textvariable=self.x,
                               width=4)
        self.r_x_input.grid(row=3, column=1, padx=5, pady=5)

        self.r_y_label = Label(self.__r_settings_frame, text="Real Y =")
        self.r_y_label.grid(row=4, column=0, padx=5, pady=5)
        self.y = StringVar(self.__r_settings_frame, "0")
        self.r_y_input = Entry(self.__r_settings_frame,
                               textvariable=self.y,
                               width=4)
        self.r_y_input.grid(row=4, column=1, padx=5, pady=5)

        self.__calculer_result = Button(self.__r_settings_frame,
                                        text="Positioning",
                                        command=self.get_result)
        self.__calculer_result.grid(row=5, column=0, padx=5, pady=5)

        self.__d_view_status = IntVar()
        self.__d_view_status.set(0)
        self.__d_view_switch = Checkbutton(self.__r_settings_frame,
                                           text="Detail",
                                           variable=self.__d_view_status,
                                           command=self.d_view_change)
        self.__d_view_switch.grid(row=5, column=1, padx=5, pady=5)

        self.algomenu = Menu(self.menubar, tearoff=False)
        self.algomenu.add_command(label="All Tx", command=self.set_algo_all_tx)
        self.algomenu.add_command(
            label="3 Max Tx",
            command=self.set_algo_3_max_tx)
        self.algomenu.add_command(label="Other algorithm")
        self.algomenu.add_command(label="Exit", command=self.dest)
        self.menubar.add_cascade(label="Algorithm", menu=self.algomenu)

        self.config(menu=self.menubar)

        self.__import_fichier = Button(self.__r_settings_frame,
                                        text="Positioning",
                                        command=self.read_from_file)
        self.__import_fichier.grid(row=6, column=0, padx=5, pady=5)
        self.__import_fichier.grid_forget()

        self.__receive_signal = Button(self.__r_settings_frame,
                                        text="Record",
                                        command=self.pd_record_from_rasp)
        self.__receive_signal.grid(row=6, column=1, padx=5, pady=5)

        self.pd_t_label = Label(self.__r_settings_frame, text="Receive seconds")
        self.pd_t_label.grid(row=7, column=0, padx=5, pady=5)
        self.pd_t = StringVar(self.__r_settings_frame, "10")
        self.pd_t_input = Entry(self.__r_settings_frame,
                               textvariable=self.pd_t,
                               width=4)
        self.pd_t_input.grid(row=7, column=1, padx=5, pady=5)

        self.pd_f_label = Label(self.__r_settings_frame, text="Sample rate (Hz)")
        self.pd_f_label.grid(row=7, column=2, padx=5, pady=5)
        self.pd_f = StringVar(self.__r_settings_frame, "44100")#"3000000")
        self.pd_f_input = Entry(self.__r_settings_frame,
                               textvariable=self.pd_f,
                               width=8)
        self.pd_f_input.grid(row=7, column=3, padx=5, pady=5)

        self.input_device_index_label = Label(self.__r_settings_frame, text="Input device index")
        self.input_device_index_label.grid(row=8, column=0, padx=5, pady=5)
        self.input_device_index = StringVar(self.__r_settings_frame, "2")
        self.input_device_index_input = Entry(self.__r_settings_frame,
                               textvariable=self.input_device_index,
                               width=4)
        self.input_device_index_input.grid(row=8, column=1, padx=5, pady=5)

        self.wave_output_filename_label = Label(self.__r_settings_frame, text="Wave output filename")
        self.wave_output_filename_label.grid(row=8, column=2, padx=5, pady=5)
        self.wave_output_filename = StringVar(self.__r_settings_frame, "output.wav")
        self.wave_output_filename_input = Entry(self.__r_settings_frame,
                               textvariable=self.wave_output_filename,
                               width=8)
        self.wave_output_filename_input.grid(row=8, column=3, padx=5, pady=5)

        self.signal_begin_label = Label(self.__r_settings_frame, text="Signal begin ? (seconds)")
        self.signal_begin_label.grid(row=1, column=2, padx=5, pady=5)
        self.signal_begin = StringVar(self.__r_settings_frame, "5")
        self.signal_begin_input = Entry(self.__r_settings_frame,
                               textvariable=self.signal_begin,
                               width=4)
        self.signal_begin_input.grid(row=1, column=3, padx=5, pady=5)

        self.signal_end_label = Label(self.__r_settings_frame, text="Signal end ? (seconds)")
        self.signal_end_label.grid(row=2, column=2, padx=5, pady=5)
        self.signal_end = StringVar(self.__r_settings_frame, "10")
        self.signal_end_input = Entry(self.__r_settings_frame,
                               textvariable=self.signal_end,
                               width=4)
        self.signal_end_input.grid(row=2, column=3, padx=5, pady=5)

        self.N1s_label = Label(self.__r_settings_frame, text="Estimated points in 1 second")
        self.N1s_label.grid(row=3, column=2, padx=5, pady=5)
        self.N1sv = StringVar(self.__r_settings_frame, "1")
        self.N1s_input = Entry(self.__r_settings_frame,
                               textvariable=self.N1sv,
                               width=4)
        self.N1s_input.grid(row=3, column=3, padx=5, pady=5)
