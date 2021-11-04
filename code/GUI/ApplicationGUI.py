import sys
import threading
import tkinter as tk
from cefpython3 import cefpython as cef
from PIL import Image, ImageTk
from GUI.ClassifierBrowser import ClassifierBrowser


class ApplicationGUI(tk.Frame):
    def __init__(self, root, process_manager):
        self.main_height = 800
        self.main_width = 450
        self.__process_manager = process_manager

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

        # Logo
        logo = Image.open('resources/images/Google_Play-Logo.wine.png')
        logo = logo.resize((self.main_width, int(self.main_width / 3)))
        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(image=logo)
        logo_label.image = logo
        logo_label.grid(column=1, row=0)

        self.menu_button_width = 49
        self.menu_button_height = 3

        # Dataset Button
        self.new_dataset_button = tk.Button(root, text='Load data from kaggle_dataset',
                                            width=self.menu_button_width, height=self.menu_button_height,
                                            bg="#3bccff", font="Raleway",
                                            command=self.new_dataset_command)
        self.new_dataset_button.grid(column=1, row=1)

        # Dataset Button
        self.old_dataset_button = tk.Button(root, text='Load data from old dataset',
                                            width=self.menu_button_width, height=self.menu_button_height,
                                            bg="#48ff48", font="Raleway",
                                            command=self.old_dataset_command)
        self.old_dataset_button.grid(column=1, row=2)

        # Data Miner Button
        self.data_miner_button = tk.Button(root, text='Retrieve data from google play',
                                           width=self.menu_button_width, height=self.menu_button_height,
                                           bg="#ffd400", font="Raleway", command=self.data_miner_command)
        self.data_miner_button.grid(column=1, row=3)

        # Manual classification Button
        self.manual_classify_button = tk.Button(root, text='Classify applications manually',
                                                width=self.menu_button_width, height=self.menu_button_height,
                                                bg="#ff3333", font="Raleway", command=self.manual_classify_command)
        self.manual_classify_button.grid(column=1, row=4)

        # Data Miner Button
        self.auto_classify_button = tk.Button(root, text='Automatic apps classification',
                                              width=self.menu_button_width, height=self.menu_button_height,
                                              bg="#3bccff", font="Raleway", command=self.auto_classify_command)
        self.auto_classify_button.grid(column=1, row=5)

        # Exit Button
        exit_button = tk.Button(root, text='Exit', width=self.menu_button_width, height=self.menu_button_height,
                                font="Raleway", command=self.exit_button_command)
        exit_button.grid(column=1, row=6)

        tk.Frame.__init__(self, root)

    def data_miner_command(self):
        self.data_miner_button.config(state='disabled')
        self.__data_miner_button_thread = threading.Thread(target=self.__process_manager.launch_data_miner)
        self.__data_miner_button_thread.start()
        self.__data_miner_button_thread.join()
        # self.data_miner_button.config(state='normal')

    def new_dataset_command(self):
        self.new_dataset_button.config(state='disabled')
        self.__new_dataset_button_thread = threading.Thread(target=self.__process_manager.launch_new_dataset)
        self.__new_dataset_button_thread.start()
        self.__new_dataset_button_thread.join()

    def old_dataset_command(self):
        self.old_dataset_button.config(state='disabled')
        self.__old_dataset_button_thread = threading.Thread(target=self.__process_manager.launch_old_dataset)
        self.__old_dataset_button_thread.start()
        self.__old_dataset_button_thread.join()

    def manual_classify_command(self):
        self.__manual_classifier_thread = threading.Thread(target=self.manual_classify_window())
        self.__manual_classifier_thread.start()
        self.__manual_classifier_thread.join()

    def auto_classify_command(self):
        self.__auto_classifier_thread = threading.Thread(target=self.__process_manager.do_classification_dataset)
        self.__auto_classifier_thread.start()
        self.__auto_classifier_thread.join()

    def manual_classify_window(self):
        self.root.update()
        mc_window = tk.Toplevel(self)

        x_coordinate = int((self.screen_width / 2) - 600)
        y_coordinate = int((self.screen_height / 2))
        mc_window.geometry(f"{1200}x{800}+{x_coordinate}+{y_coordinate}")

        window = ClassifierBrowser(mc_window, None)

    def exit_button_command(self):
        self.root.destroy()


if __name__ == '__main__':
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    root = tk.Tk()
    app = ApplicationGUI(root)
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    cef.Initialize()
    app.mainloop()
    cef.Shutdown()
