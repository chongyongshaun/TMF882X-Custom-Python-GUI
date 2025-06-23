from tkinter import *
from tkinter import messagebox

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
            else:
                ErrorMsg = f"Failure to estabish UART connection using {self.clicked_com.get()} "
                messagebox.showerror("showerror", ErrorMsg)
        else:

            # Closing the Serial COM
            # Close the serial communication
            self.serial.SerialClose(self)

            InfoMsg = f"UART connection using {self.clicked_com.get()} is now closed"
            messagebox.showwarning("showinfo", InfoMsg)
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] = "active"
            self.drop_baud["state"] = "active"
            self.drop_com["state"] = "active"



if __name__ == "__main__": #make sure this only runs when this file is run directly
    RootGUI()
    ComGUI()