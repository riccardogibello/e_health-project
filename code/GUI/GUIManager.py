from threading import Thread

from GUI.DashComponents.DashManagerComponent import run_dash
from GUI.WindowComponents.GenericWindow import GenericWindow
from GUI.WindowComponents.HomePageWindow import HomePageWindow
from GUI.WindowComponents.ManualClassifierWindow import ManualClassifierWindow
from GUI.WindowComponents.DashboardWindow import OverviewDashboardWindow
from GUI.WindowComponents.WaitingWindow import WaitingWindow


class GUIManager:
    def __init__(self, process_manager):
        self.process = None
        self.window = None
        self.process_manager = process_manager
        self.go_to_home_page()

        self.page = 0
        self.params = None

        self.message = ''

    def go_to_home_page(self):
        if self.window:
            self.window.close()
        self.window = HomePageWindow(self)
        self.window.show()

    def go_to_manual_classifier_page(self):
        if self.window:
            self.window.close()
        self.window = ManualClassifierWindow(self)
        self.window.show()

    def go_to_waiting_page(self, message, go_back_button_text, number_labels):
        if self.window:
            self.window.close()
        self.window = WaitingWindow(self, message, go_back_button_text, number_labels)
        self.window.show()

    def go_to_generic_page(self, message):
        if self.window:
            self.window.close()
        self.window = GenericWindow(self, message)
        self.message = ''
        self.window.show()

    def go_to_dashboard(self):
        if self.window:
            self.window.close()

        self.process = Thread(target=run_dash)
        self.process.start()

        self.window = OverviewDashboardWindow(self, self.process)
        self.window.show()
