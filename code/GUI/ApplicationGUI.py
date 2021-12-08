import sys
import threading
import tkinter as tk
import tkinter.font

from cefpython3 import cefpython as cef
from PIL import Image, ImageTk
from GUI.HomePage import HomePage
from GUI.ProcessManager import ProcessManager


class ApplicationGUI(tk.Frame):
    def __init__(self, root, process_manager):
        super().__init__()
        self.homepage = None
        self.font = tkinter.font.Font(family="Calibri", size=16, weight="normal")

        self.main_height = 800
        self.main_width = 450
        self.__process_manager = ProcessManager()

        # Screen Information
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenmmheight()

        # button threads
        # needed to launch processes otherwise the GUI freezes until process completion
        self.__data_miner_button_thread = None
        self.__new_dataset_button_thread = None
        self.__old_dataset_button_thread = None
        self.__manual_classifier_thread = None
        self.__auto_classifier_thread = None

        # Root
        self.root = root
        self.root.config(bg='white')
        self.root.title("Google Play - Serious Games Finder")
        self.root.resizable(False, False)
        self.create_homepage()

    def create_homepage(self):
        self.homepage = HomePage(self)

    def destroy_homepage(self):
        self.homepage.destroy()

    def get_process_manager(self):
        return self.__process_manager

    def destroy_graphic(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.update()



if __name__ == '__main__':
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    root = tk.Tk()
    app = ApplicationGUI(root)
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    cef.Initialize()
    app.mainloop()
    cef.Shutdown()
