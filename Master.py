from GUI_Master import RootGUI, ComGUI


RootMaster = RootGUI()
ComMaster = ComGUI(RootMaster.root)

RootMaster.root.mainloop()