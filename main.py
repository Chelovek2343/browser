from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QWidget, QTabWidget, QAction, QFileDialog, QToolBar, QComboBox, QListWidget, QShortcut, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem, QWebEngineProfile, QWebEnginePage
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QKeySequence
import sys, json, os, speech_recognition as sr


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.setProfile(profile)


class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Custom Web Browser')
        self.setGeometry(100, 100, 1200, 800)
        self.homepage = self.load_custom_homepage()
        self.bookmarks = []
        self.incognito_mode = False
        self.history_file = "history.json"
        self.history = self.load_history()
        self.downloads = []

        # Search engines
        self.search_engines = {
            'Google': 'https://www.google.com/search?q={}',
            'Bing': 'https://www.bing.com/search?q={}',
            'DuckDuckGo': 'https://duckduckgo.com/?q={}'
        }
        self.selected_search_engine = 'Google'

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Bookmark Action
        bookmark_action = QAction('Save Bookmark', self)
        bookmark_action.triggered.connect(self.save_bookmark)
        file_menu.addAction(bookmark_action)

        # Set Custom Homepage Action
        set_homepage_action = QAction('Set Custom Homepage', self)
        set_homepage_action.triggered.connect(self.set_custom_homepage)
        file_menu.addAction(set_homepage_action)

        # Download Manager Action
        download_manager_action = QAction('Download Manager', self)
        download_manager_action.triggered.connect(self.show_download_manager)
        file_menu.addAction(download_manager_action)

        # Toolbar Setup
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Navigation buttons
        self.back_button = QPushButton('Back')
        self.forward_button = QPushButton('Forward')
        self.reload_button = QPushButton('Reload')
        self.incognito_button = QPushButton('Incognito Mode')

        # History dropdown
        self.history_dropdown = QComboBox()
        self.history_dropdown.addItem('History')
        self.update_history_dropdown()  # Fill the history dropdown with existing history

        # Search engine dropdown
        self.search_dropdown = QComboBox()
        self.search_dropdown.addItems(['Google', 'Bing', 'DuckDuckGo'])

        # New tab button and voice search button
        self.new_tab_button = QPushButton('+')
        self.voice_search_button = QPushButton('🎤')  # Voice search button

        # Connect buttons to methods
        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)
        self.reload_button.clicked.connect(self.reload_page)
        self.incognito_button.clicked.connect(self.toggle_incognito_mode)
        self.history_dropdown.activated[str].connect(self.load_from_history)  # Fix: Using correct method for history dropdown
        self.new_tab_button.clicked.connect(self.new_tab)
        self.search_dropdown.activated[str].connect(self.update_search_engine)
        self.voice_search_button.clicked.connect(self.voice_search)  # Connect voice search

        # Add buttons to toolbar
        self.toolbar.addWidget(self.back_button)
        self.toolbar.addWidget(self.forward_button)
        self.toolbar.addWidget(self.reload_button)
        self.toolbar.addWidget(self.incognito_button)
        self.toolbar.addWidget(self.search_dropdown)
        self.toolbar.addWidget(self.history_dropdown)
        self.toolbar.addWidget(self.new_tab_button)
        self.toolbar.addWidget(self.voice_search_button)  # Add voice button

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)  # Fix here
        self.setCentralWidget(self.tabs)

        self.new_tab()

        # Enable drag and drop
        self.tabs.setMovable(True)

        # Keyboard Shortcuts
        self.add_shortcut(QKeySequence("Ctrl+T"), self.new_tab)
        self.add_shortcut(QKeySequence("Ctrl+W"), self.close_current_tab)
        self.add_shortcut(QKeySequence("Ctrl+L"), self.voice_search)  # Voice search shortcut

        # Shortcuts for tab navigation (Ctrl+1 to Ctrl+9)
        for i in range(1, 10):
            self.add_shortcut(QKeySequence(f"Ctrl+{i}"), lambda index=i: self.switch_tab(index-1))

    def handle_download(self, download: QWebEngineDownloadItem):
        """Handle download request."""
        download.accept()
        download.setPath(os.path.join(os.getcwd(), download.fileName()))
        download.finished.connect(self.download_finished)

        # Save download information
        self.downloads.append(download.fileName())
        self.show_download_manager()

    def download_finished(self):
        """Called when a download finishes."""
        print("Download finished.")

    def update_history_dropdown(self):
        """Update the history dropdown with the history list."""
        for url in self.history:
            self.history_dropdown.addItem(url)

    def load_from_history(self, url):
        """Load the selected history item in the current tab."""
        print(f"Loading from history: {url}")
        browser = self.tabs.currentWidget().layout().itemAt(1).widget()  # Get the current browser
        browser.setUrl(QUrl(url))

    def show_download_manager(self):
        """Open a simple download manager dialog."""
        download_manager_dialog = QDialog(self)
        download_manager_dialog.setWindowTitle('Download Manager')
        download_manager_dialog.setGeometry(200, 200, 400, 300)

        # List widget to display downloads
        download_list = QListWidget(download_manager_dialog)
        download_list.setGeometry(10, 10, 380, 250)

        # Add all current downloads to the list
        for download in self.downloads:
            download_list.addItem(download)

        download_manager_dialog.exec_()

    def set_custom_homepage(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("HTML Files (*.html);;All Files (*)")

        if file_dialog.exec_():
            homepage_path = file_dialog.selectedFiles()[0]
            with open("custom_homepage.txt", "w") as file:
                file.write(homepage_path)
            self.homepage = homepage_path
            print(f'Custom homepage set: {homepage_path}')

    def add_shortcut(self, key_sequence, callback):
        shortcut = QShortcut(key_sequence, self)
        shortcut.activated.connect(callback)

    def new_tab(self, url=None):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        url_bar = QLineEdit()
        url_bar.setPlaceholderText('Enter URL and press Enter...')
        url_bar.returnPressed.connect(lambda: self.load_url(browser, url_bar))
        layout.addWidget(url_bar)

        browser = QWebEngineView()
        if self.incognito_mode:
            # Create a new profile for incognito mode
            profile = QWebEngineProfile("IncognitoProfile", self)
            profile.setRequestInterceptor(None)
            page = CustomWebEnginePage(profile)
            browser.setPage(page)
        else:
            page = QWebEnginePage(QWebEngineProfile.defaultProfile())
            browser.setPage(page)

        browser.page().profile().downloadRequested.connect(self.handle_download)
        layout.addWidget(browser)

        if not url:
            url = self.homepage
        browser.setUrl(QUrl(url))

        self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentWidget(tab)

    def load_url(self, browser, url_bar):
        url = url_bar.text()
        if not url.startswith('http'):
            search_url = self.search_engines[self.selected_search_engine].format(url)
            browser.setUrl(QUrl(search_url))
        else:
            browser.setUrl(QUrl(url))
        if not self.incognito_mode:
            self.history.append(url)
            self.save_history()
            self.update_history_dropdown()  # Update dropdown with new history

    def voice_search(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                query = recognizer.recognize_google(audio).strip()
                print(f"Recognized: {query}")

                if query.startswith("http") or "." in query:
                    url = query if query.startswith("http") else "http://" + query
                    self.new_tab(url)
                else:
                    search_url = self.search_engines[self.selected_search_engine].format(query)
                    self.new_tab(search_url)

            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError:
                print("Speech recognition service is unavailable")

    def save_bookmark(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        url = current_browser.url().toString()
        self.bookmarks.append(url)
        with open("bookmarks.json", "w") as file:
            json.dump(self.bookmarks, file)
        print(f'Bookmark saved: {url}')

    def go_back(self):
        self.tabs.currentWidget().layout().itemAt(1).widget().back()

    def go_forward(self):
        self.tabs.currentWidget().layout().itemAt(1).widget().forward()

    def reload_page(self):
        self.tabs.currentWidget().layout().itemAt(1).widget().reload()

    def toggle_incognito_mode(self):
        self.incognito_mode = not self.incognito_mode
        self.incognito_button.setText('Incognito Mode (ON)' if self.incognito_mode else 'Incognito Mode (OFF)')
        print("Incognito Mode:", "Enabled" if self.incognito_mode else "Disabled")

    def update_search_engine(self, engine):
        self.selected_search_engine = engine
        print(f'Search engine updated to: {self.selected_search_engine}')

    def save_history(self):
        if not self.incognito_mode:
            with open(self.history_file, "w") as file:
                json.dump(self.history, file)

    def load_history(self):
        return json.load(open(self.history_file)) if os.path.exists(self.history_file) else []

    def load_custom_homepage(self):
        return open("custom_homepage.txt").read().strip() if os.path.exists("custom_homepage.txt") else "https://www.google.com"

    def close_tab(self, index):
        """Close the tab at the specified index."""
        self.tabs.removeTab(index)

    def close_current_tab(self):
        """Close the currently active tab."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            self.tabs.removeTab(current_index)

    def switch_tab(self, index):
        """Switch to the tab at the specified index."""
        if index >= 0 and index < self.tabs.count():
            self.tabs.setCurrentIndex(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebBrowser()
    window.show()
    sys.exit(app.exec_())
