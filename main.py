from cefpython3 import cefpython as cef

from DataManagers.OldDatasetManager import *
from ProcessManager import ProcessManager
from DataManagers.DataMiner import DataMiner
from DataManagers.WordsMiner import *
import tkinter as tk
from GUI.ApplicationGUI import ApplicationGUI

#word_miner = WordsMiner({'wikipage': 'https://en.wikipedia.org/wiki/Serious_game',
#                         'paper_1': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5222787/pdf/fpsyt-07'
#                                    '-00215.pdf',
#                         'paper_2': 'https://www.hindawi.com/journals/ijcgt/2014/787968/'})


def launch_data_miner():
    miner = DataMiner()
    miner.fill_database()


def launch_new_dataset_manager():
    pass
    # new_dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    # new_dataset_manager.load_apps_into_db()


def launch_old_dataset_manager():
    old_dataset_manager = OldDatasetManager()
    old_dataset_manager.load_old_dataset_into_db()


def launch_words_miner():
    pass
    # word_miner.find_serious_games_words()


if __name__ == '__main__':
    process_manager = ProcessManager()
    root = tk.Tk()
    app = ApplicationGUI(root, process_manager)
    cef.Initialize()
    app.mainloop()
    cef.Shutdown()

    process_manager.close_application()

    # sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # root = tk.Tk()
    # app = MainFrame(root)
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    # cef.Initialize()
    # app.after(0, lambda: print('ciao'))
    # app.mainloop()
    # cef.Shutdown()
