from GUI_Master import RootGUI, ComGUI
from Serial_COM_Ctrl import SerialCtrl

SerialCtrl = SerialCtrl()
RootMaster = RootGUI()
ComMaster = ComGUI(RootMaster.root, SerialCtrl)

RootMaster.root.mainloop()