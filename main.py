import os
import signal
import sys
from multiprocessing.pool import ThreadPool
from PyQt5.QtWidgets import QApplication
from GUI.GUIManager import GUIManager
from GUI.ProcessHandler import ProcessHandler


def create_process_manager_thread():
    return ProcessHandler()


if __name__ == '__main__':
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(create_process_manager_thread)
    proc_man = async_result.get()

    app = QApplication(sys.argv)
    gui_manager = GUIManager(process_manager=proc_man)

    app.exec()

    proc_man.close_application()
    os.kill(os.getpid(), signal.SIGTERM)  # this was forcefully added to stop also the dash app that is once started
