import sys
import threading
import tkinter as tk
import tkinter.font

from cefpython3 import cefpython as cef
from PIL import Image, ImageTk
from GUI.ClassifierBrowser import ClassifierBrowser


class HomePage:
    def __init__(self, application_gui):
        root = application_gui.root
        root.geometry("450x585")
        self.__auto_classifier_thread = None
        self.__manual_classifier_thread = None
        self.__new_dataset_button_thread = None
        self.__old_dataset_button_thread = None
        self.__data_miner_button_thread = None
        self.ApplicationGUI = application_gui

        # Logo
        logo = Image.open('resources/images/Google_Play-Logo.wine.png')
        logo = logo.resize((self.ApplicationGUI.main_width, int(self.ApplicationGUI.main_width / 3)))
        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(image=logo)
        logo_label.image = logo
        logo_label.grid(column=1, row=0)

        self.menu_button_width = 41
        self.menu_button_height = 2

        # Dataset Button
        self.new_dataset_button = tk.Button(self.ApplicationGUI.root,
                                            text='Load data from new dataset',
                                            width=self.menu_button_width,
                                            height=self.menu_button_height,
                                            bg="#3bccff",
                                            font=self.ApplicationGUI.font,
                                            command=self.new_dataset_command)
        self.new_dataset_button.grid(column=1, row=1)

        # Dataset Button
        self.old_dataset_button = tk.Button(self.ApplicationGUI.root,
                                            text='Load data from old dataset',
                                            width=self.menu_button_width,
                                            height=self.menu_button_height,
                                            bg="#48ff48",
                                            font=self.ApplicationGUI.font,
                                            command=self.old_dataset_command)
        self.old_dataset_button.grid(column=1, row=2)

        # Data Miner Button
        self.data_miner_button = tk.Button(self.ApplicationGUI.root,
                                           text='Retrieve data from google play',
                                           width=self.menu_button_width,
                                           height=self.menu_button_height,
                                           bg="#ffd400",
                                           font=self.ApplicationGUI.font,
                                           command=self.data_miner_command)
        self.data_miner_button.grid(column=1, row=3)

        # Manual classification Button
        self.manual_classify_button = tk.Button(self.ApplicationGUI.root,
                                                text='Classify applications manually',
                                                width=self.menu_button_width,
                                                height=self.menu_button_height,
                                                bg="#ff3333",
                                                font=self.ApplicationGUI.font,
                                                command=self.manual_classify_command)
        self.manual_classify_button.grid(column=1, row=4)

        # Data Miner Button
        self.auto_classify_button = tk.Button(self.ApplicationGUI.root,
                                              text='Automatic apps classification',
                                              width=self.menu_button_width,
                                              height=self.menu_button_height,
                                              bg="#3bccff",
                                              font=self.ApplicationGUI.font,
                                              command=self.auto_classify_command)
        self.auto_classify_button.grid(column=1, row=5)

        # Exit Button
        exit_button = tk.Button(self.ApplicationGUI.root,
                                text='Exit',
                                width=self.menu_button_width,
                                height=self.menu_button_height,
                                font=self.ApplicationGUI.font,
                                command=self.exit_button_command)
        exit_button.grid(column=1, row=6)

        self.frame = tk.Frame(self.ApplicationGUI.root)

    def destroy(self):
        for widget in self.ApplicationGUI.root.winfo_children():
            widget.destroy()

        self.ApplicationGUI.root.update()

    def data_miner_command(self):
        self.data_miner_button.config(state='disabled')
        self.__data_miner_button_thread = threading.Thread(
            target=self.ApplicationGUI.get_process_manager().launch_data_miner)

        self.__data_miner_button_thread.start()
        self.__data_miner_button_thread.join()
        # self.data_miner_button.config(state='normal')

    def new_dataset_command(self):
        self.new_dataset_button.config(state='disabled')
        self.__new_dataset_button_thread = threading.Thread(
            target=self.ApplicationGUI.get_process_manager().launch_new_dataset)
        self.__new_dataset_button_thread.start()
        self.__new_dataset_button_thread.join()

    def old_dataset_command(self):
        self.old_dataset_button.config(state='disabled')
        self.__old_dataset_button_thread = threading.Thread(
            target=self.ApplicationGUI.get_process_manager().launch_old_dataset)
        self.__old_dataset_button_thread.start()
        self.__old_dataset_button_thread.join()

    def manual_classify_command(self):
        #self.__manual_classifier_thread = threading.Thread(target=self.manual_classify_window)
        self.destroy()
        self.manual_classify_window()
        #self.__manual_classifier_thread.start()
        #self.__manual_classifier_thread.join()

    def auto_classify_command(self):
        self.__auto_classifier_thread = threading.Thread(
            target=self.ApplicationGUI.get_process_manager().do_classification_dataset)
        self.__auto_classifier_thread.start()
        self.__auto_classifier_thread.join()

    def manual_classify_window(self):
        window = ClassifierBrowser(self.ApplicationGUI, None)

    def exit_button_command(self):
        self.ApplicationGUI.root.destroy()
