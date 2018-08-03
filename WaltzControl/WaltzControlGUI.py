from tkinter import Tk
import waltz_GUI_class
import matplotlib.pyplot as plt


def main():
    root = Tk()
    waltz = waltz_GUI_class.WaltzGUI(root)
    def close_window():
        """Defines which actions to call when window is destroyed.
        """
        plt.close('all')
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", close_window)
    root.mainloop() 
    
main()
