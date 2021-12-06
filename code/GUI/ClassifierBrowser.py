import tkinter.messagebox

from cefpython3 import cefpython as cef
import ctypes
import tkinter as tk
import platform
from GUI.ManualClassifier import ManualClassifier

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")


# Globals
# logger = _logging.getLogger("tkinter_.py")


class ClassifierBrowser(tk.Frame):

    def __init__(self, root, classifier):
        self.browser_frame = None
        self.navigation_bar = None
        self.default_page = None
        self.classifier = classifier

        # Root
        root.geometry("1200x800")
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)

        # MainFrame
        tk.Frame.__init__(self, root)
        self.master.title("Serious Game manual classifier")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)
        self.bind("<Configure>", self.on_configure)

        # NavigationBar
        self.navigation_bar = NavigationBar(self)
        self.navigation_bar.grid(row=0, column=0)
        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)

        # BrowserFrame
        self.browser_frame = BrowserFrame(self, self.default_page, self.navigation_bar)
        self.browser_frame.grid(row=1, column=0,
                                sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def create_new_browser(self, page):
        self.browser_frame = BrowserFrame(self, page, self.navigation_bar)
        self.browser_frame.grid(row=1, column=0,
                                sticky=(tk.N + tk.S + tk.E + tk.W))
        self.update()

    def on_root_configure(self, _):
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        if self.browser_frame:
            width = event.width
            height = event.height
            if self.navigation_bar:
                height = height - self.navigation_bar.winfo_height()
            self.browser_frame.on_mainframe_configure(width, height)

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
        self.master.destroy()

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None


class BrowserFrame(tk.Frame):

    def __init__(self, master, page, navigation_bar=None):
        self.page = page
        self.navigation_bar = navigation_bar
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        self.bind("<Configure>", self.on_configure)
        navigation_bar.focus_force()

    def embed_browser(self, page):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url=page)
        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        elif MAC:
            from AppKit import NSApp
            import objc
            return objc.pyobjc_id(NSApp.windows()[-1].contentView())
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser(self.page)

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        self.destroy()

    ###
    def destroy_browser(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()

    def clear_browser_references(self):
        self.browser = None


class NavigationBar(tk.Frame):
    def __init__(self, master):
        self.not_serious_state = tk.NONE
        self.serious_state = tk.NONE
        # Classifier variables
        self.app_classifier = None
        self.current_id = None
        self.start_stop_button_status = None

        tk.Frame.__init__(self, master)

        # Start Entry
        start_text = tk.StringVar(self, value='start')
        self.start_entry = tk.Entry(self, textvariable=start_text)
        self.start_entry.grid(row=0, column=0)
        self.start_entry.config(state=tk.NORMAL)

        # End Entry
        self.end_text = tk.StringVar(self, value='end')
        self.end_entry = tk.Entry(self, textvariable=self.end_text)
        self.end_entry.grid(row=0, column=1)
        self.end_entry.config(state='normal')

        # Serious button
        self.serious_image = tk.PhotoImage(file='resources/images/serious_button.png')
        self.serious_button = tk.Button(self, image=self.serious_image, command=self.serious_function)
        self.serious_button.grid(row=0, column=2)
        self.serious_button.config(state='disabled')

        # Start/Stop button
        self.start_image = tk.PhotoImage(file='resources/images/start_image.png')
        self.start_stop_button = tk.Button(self, image=self.start_image, command=self.start_stop_function)
        self.start_stop_button.grid(row=0, column=3)

        # Not Serious button
        self.not_serious_image = tk.PhotoImage(file='resources/images/not_serious_button.png')
        self.not_serious_button = tk.Button(self, image=self.not_serious_image, command=self.not_serious_function)
        self.not_serious_button.config(state='disabled')
        self.not_serious_button.grid(row=0, column=4)

        self.stop_image = tk.PhotoImage(file='resources/images/stop_image.png')

    def start_stop_function(self):
        try:
            start = int(self.start_entry.get())
            end = int(self.end_entry.get())
        except ValueError:
            tk.messagebox.showerror("Wrong Value!", "Illegal values inserted", parent=self)
            return

        if start >= end:
            tkinter.messagebox.showerror("Range Error", "Check range values!", parent=self)
            return
        if not self.app_classifier:
            self.app_classifier = ManualClassifier(start, end)

        if self.start_stop_button_status:
            self.start_stop_button_status = False
            self.start_stop_button.configure(image=self.start_image)
            self.not_serious_button.config(state='disabled')
            self.serious_button.config(state='disabled')
            self.app_classifier = None


        else:
            self.start_stop_button.config(state='disabled')
            self.not_serious_button.config(state='normal')
            self.serious_button.config(state='normal')

            self.start_stop_button.configure(image=self.stop_image)
            self.start_stop_button.config(state='normal')
            self.start_stop_button_status = True

            self.current_id = self.app_classifier.get_app_to_classify()[1]
            url_to_load = self.app_classifier.get_app_to_classify()[0]
            if not url_to_load:
                return
            self.master.get_browser().LoadUrl(url_to_load)

    def not_serious_function(self):
        self.classify_button(False)

    def serious_function(self):
        self.classify_button(True)

    def classify_button(self, evaluation):
        self.app_classifier.classify_app_as_serious(self.current_id, evaluation)

        self.current_id = self.app_classifier.get_app_to_classify()[1]
        url_to_load = self.app_classifier.get_app_to_classify()[0]
        if not url_to_load:
            self.master.get_browser().close()
            self.master.master.destroy()
            return
        self.master.get_browser().LoadUrl(url_to_load)
