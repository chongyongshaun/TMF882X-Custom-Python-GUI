import queue
import time
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from TMF882X_Data_Reader import DataReader
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class RootGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Serial Communication GUI")
        self.root.geometry("360x120")
        self.root.config(bg="white")

class ComGUI:
    def __init__(self, root, serial):
        self.root = root
        self.serial = serial
        self.frame = LabelFrame(root, text="COM Manager", padx=5, pady=5, bg="white")
        self.label_com = Label(self.frame, text="Available Ports:", bg="white", width=15, anchor="w")
        self.label_bd = Label(self.frame, text="Baud Rate:", bg="white", width=15, anchor="w")
        self.ComOptionMenu()
        self.baudOptionMenu()

        self.btn_refresh = Button(self.frame, text="Refresh", width=10, command=self.com_refresh)
        self.btn_connect = Button(self.frame, text="Connect", width=10, state="disabled", command=self.serial_connect)

        self.padx = 20
        self.pady = 5
        self.publish()

    def ComOptionMenu(self):
        coms = self.serial.getComPorts()
        self.clicked_com = StringVar() 
        self.clicked_com.set(coms[0])
        self.drop_com = OptionMenu(self.frame, self.clicked_com, *coms, command=self.connect_ctrl)
        self.drop_com.config(width=10)

    def baudOptionMenu(self):
        '''
         Method to list all the baud rates in a drop menu
        '''
        self.clicked_bd = StringVar()
        bds = ["-",
               "300",
               "600",
               "1200",
               "2400",
               "4800",
               "9600",
               "14400",
               "19200",
               "28800",
               "38400",
               "56000",
               "57600",
               "115200",
               "128000",
               "256000",
               "1000000"]
        self.clicked_bd .set(bds[0])
        self.drop_baud = OptionMenu(self.frame, self.clicked_bd, *bds, command=self.connect_ctrl)
        self.drop_baud.config(width=10)

    def publish(self):
        self.frame.grid(row=0, column=0, padx=5, pady=5, columnspan=3, rowspan=3)
        self.label_com.grid(row=2, column=1)
        self.drop_com.grid(row=2, column=2)
        self.btn_refresh.grid(row=2, column=3)
        self.label_bd.grid(row=3, column=1)
        self.drop_baud.grid(row=3, column=2)
        self.btn_connect.grid(row=3, column=3)

    def connect_ctrl(self, *args):
        '''
        Method to control the connect button
        '''
        if self.clicked_com.get() == "-" or self.clicked_bd.get() == "-":
            self.btn_connect.config(state="disabled")
        else:
            self.btn_connect.config(state="normal")

    def com_refresh(self):
        self.drop_com.destroy()
        self.ComOptionMenu() #recreate self.drop_com which is a OptionMenu object
        self.drop_com.grid(row=2, column=2) #republish the new drop menu

        self.connect_ctrl() #recheck the connect button state

        print("Refreshing COM ports...")
        
    def serial_connect(self):
        '''
        Method that Updates the GUI during connect / disconnect status
        Manage serials and data flows during connect / disconnect status
        '''
        print(f"Connecting to {self.clicked_com.get()} at {self.clicked_bd.get()} baud...") #placeholder
        if self.btn_connect["text"] in "Connect":
            # Start the serial communication
            self.serial.SerialOpen(self)

            # If connection established move on
            if self.serial.ser.status:
                # Update the COM manager
                self.btn_connect["text"] = "Disconnect"
                self.btn_refresh["state"] = "disable"
                self.drop_baud["state"] = "disable"
                self.drop_com["state"] = "disable"
                InfoMsg = f"Successful UART connection using {self.clicked_com.get()}"
                messagebox.showinfo("showinfo", InfoMsg)

                self.graph = GraphGUI(self.root, self.serial)
                # Display the channel manager
                self.conn = ConnGUI(self.root, self.serial, self.graph)
                

            else:
                ErrorMsg = f"Failure to estabish UART connection using {self.clicked_com.get()} "
                messagebox.showerror("showerror", ErrorMsg)
        else:

            # Closing the Serial COM
            # Close the serial communication
            
            self.serial.SerialClose(self)

            # Closing the Conn Manager
            # Destroy the channel manager
            self.conn.ConnGUIClose()
            self.graph.GraphGUIClose()
            self.graph.destroy_channel_selector()

            # display message and update COM GUI buttons
            InfoMsg = f"UART connection using {self.clicked_com.get()} is now closed"
            messagebox.showwarning("showinfo", InfoMsg)
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] = "active"
            self.drop_baud["state"] = "active"
            self.drop_com["state"] = "active"

class ConnGUI():
    def __init__(self, root, serial, graph):
        '''
        Initialize main Widgets for communication GUI
        '''
        self.root = root
        self.serial = serial
        self.graph = graph

        # Build ConnGui Static Elements
        self.frame = LabelFrame(root, text="Connection Manager",
                                padx=5, pady=5, bg="white", width=60)
        self.measurement_label = Label(self.frame, text="TMF Status: ", bg="white", width=15, anchor="w")
        self.measurement_status = Label(self.frame, text="Stopped", bg="white", fg="red", width=5)

        self.ch_label = Label(self.frame, text="Active channels: ", bg="white", width=15, anchor="w")
        self.ch_status = Label(self.frame, text="...", bg="white", fg="orange", width=5)

        self.btn_toogle_measurement = Button(self.frame, text="Start",
                                       width=5, command=self.toggle_measurement)
        # self.btn_stop_stream = Button(self.frame, text="Stop", state="disabled",
        #                               width=5, command=self.stop_stream)
        
        self.btn_add_chart = Button(self.frame, text="+", state="disabled",
                                    width=5, bg="white", fg="#098577",
                                    command=self.new_chart)
        self.btn_kill_chart = Button(self.frame, text="-", state="disabled",
                                     width=5, bg="white", fg="#CC252C",
                                     command=self.kill_chart)
        
        self.save = False
        self.SaveVar = IntVar()
        self.save_check = Checkbutton(self.frame, text="Save data", variable=self.SaveVar,
                                      onvalue=1, offvalue=0, bg="white", state="disabled",
                                      command=self.save_data)

        self.separator = ttk.Separator(self.frame, orient='vertical') # Only for aesthetics
 
        # Optional Graphic parameters
        self.padx = 20
        self.pady = 15

        self.ConnGUIOpen() #publishing the GUI onto the root window (and extending it)

    def ConnGUIOpen(self):
        '''
        Method to display all the widgets 
        '''
        self.root.geometry("900x600") # Extend the root window, original size is 360x120
        self.frame.grid(row=0, column=4, rowspan=3,columnspan=5, padx=5, pady=5)

        self.measurement_label.grid(column=1, row=1)
        self.measurement_status.grid(column=2, row=1)

        self.ch_label.grid(column=1, row=2)
        self.ch_status.grid(column=2, row=2, pady=self.pady)

        self.btn_toogle_measurement.grid(column=3, row=1, padx=self.padx)
        # self.btn_stop_stream.grid(column=3, row=2, padx=self.padx)

        self.btn_add_chart.grid(column=4, row=1, padx=self.padx)
        self.btn_kill_chart.grid(column=5, row=1, padx=self.padx)

        self.save_check.grid(column=4, row=2, columnspan=2)
        self.separator.place(relx=0.58, rely=0, relwidth=0.001, relheight=1)

    def ConnGUIClose(self):
        '''
        Method to close the connection GUI and destorys the widgets
        '''
        # Must destroy all the element so they are not kept in Memory
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.root.geometry("360x120")

    def toggle_measurement(self):
        if self.graph.reader.measuring:
            self.graph.reader.stop_measurement()
            self.btn_toogle_measurement.config(text="Start")
            self.measurement_status.config(text="Stopped", fg="red")
            self.save_check.config(state="disabled")
        else:
            self.graph.reader.start_measurement()
            self.btn_toogle_measurement.config(text="Stop")
            self.measurement_status.config(text="Running", fg="green")
            self.save_check.config(state="normal")

    def new_chart(self):
        pass

    def kill_chart(self):
        pass

    def save_data(self):
        pass


class GraphGUI():
    def __init__(self, root, serial):
        self.root = root
        self.serial = serial
        self.build_channel_selector()

        # Set up data queue and data reader thread
        self.data_queue = queue.Queue()
        self.selected_channels = set() 
        self.reader = DataReader(self.data_queue, self.serial, self.selected_channels)
        self.reader.start()

        self.subplots = {}  # channel_num -> (ax, bars)
        self.canvas = None

        # Set up the graph frame
        self.frame = LabelFrame(root, text="Live Histogram", padx=5, pady=5, bg="white")
        self.frame.grid(row=3, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

        self.update_plot()

    def GraphGUIClose(self):
        '''
        Method to close the graph GUI and destroy the widgets
        '''
        # Must destroy all the element so they are not kept in Memory
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.root.geometry("360x120")

        # Stop the data reader thread
        self.reader.running = False
        self.reader.join()
        

    def update_plot(self):
        while not self.data_queue.empty():
            line = self.data_queue.get()
            print(f"Line: {line}")  # Debug
            parts = line.strip().split(",")

            if len(parts) == 129 and parts[0].startswith("#RCo"):
                try:
                    channel_str = parts[0][4:]  # e.g., "#RCo2" → "2"
                    channel = int(channel_str)
                    if channel in self.selected_channels and channel in self.subplots:
                        values = np.array(list(map(int, parts[1:])))
                        ax, bars = self.subplots[channel]
                        for bar, val in zip(bars, values):
                            bar.set_height(val)
                        ax.set_ylim(0, values.max() * 1.1)
                    self.canvas.draw()
                except Exception as e:
                    print(f"Error updating plot: {e}")

        self.root.after(50, self.update_plot)

    def build_graphs_for_selected_channels(self):
        # Clear old canvas and subplots
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.subplots.clear()

        num_channels = len(self.selected_channels)
        if num_channels == 0:
            return

        # Define grid: max 3 columns
        cols = 3
        rows = (num_channels + cols - 1) // cols  # ceil division

        # Create new figure and subplots
        self.fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 2.5))
        axes = np.array(axes).reshape(-1)  # Flatten in case of 2D or 1D result

        # Only keep as many axes as needed
        axes = axes[:num_channels]

        for ax in axes:
            ax.clear()  # clear previous content

        for i, (channel, ax) in enumerate(zip(sorted(self.selected_channels), axes)):
            ax.set_title(f"Channel {channel}")
            ax.set_ylim(0, 100)
            bars = ax.bar(np.arange(128), np.zeros(128))
            self.subplots[channel] = (ax, bars)

        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    def build_channel_selector(self):
        self.channel_frame = LabelFrame(self.root, text="TDC Channel", padx=5, pady=5, bg="white")
        self.channel_frame.grid(row=7, column=0, columnspan=3, sticky="nw", padx=5, pady=5)

        # Canvas and scrollbar setup
        canvas = Canvas(self.channel_frame, height=120, bg="white")
        scrollbar = Scrollbar(self.channel_frame, orient="vertical", command=canvas.yview)
        self.inner_frame = Frame(canvas, bg="white")
        self.inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # apply button to update the selected channels
        apply_btn = Button(self.inner_frame, text="Apply", command=self.apply_selected_channels, bg="white", fg="black")
        apply_btn.pack(pady=(10, 0))
        
        # Checkboxes for channels
        self.channel_vars = []
        for i in range(10):
            var = IntVar()
            chk = Checkbutton(self.inner_frame, text=f"Channel {i}", variable=var, bg="white")
            chk.pack(anchor="w")
            self.channel_vars.append(var)

    def destroy_channel_selector(self):
        """Destroys the channel selector frame and its widgets"""
        for widget in self.channel_frame.winfo_children():
            widget.destroy()
        self.channel_frame.destroy()

    def get_selected_channels(self):
        """Returns a list of selected channel numbers"""
        return [i for i, var in enumerate(self.channel_vars) if var.get()]
    
    def apply_selected_channels(self):
        """Updates the selected channels"""
        self.selected_channels.clear()
        self.selected_channels.update(self.get_selected_channels())
        print(f"Selected channels updated: {sorted(self.selected_channels)}")

        self.build_graphs_for_selected_channels()

if __name__ == "__main__": #make sure this only runs when this file is run directly
    RootGUI()
    ComGUI()
    ConnGUI()
    GraphGUI()