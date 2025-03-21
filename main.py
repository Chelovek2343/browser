from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QWidget, QTabWidget, QAction, QFileDialog, QToolBar, QComboBox, QListWidget, QCheckBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem, QWebEngineProfile, QWebEnginePage
from PyQt5.QtCore import QUrl, QTimer
import sys, json, os

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
        self.incognito_mode = False  # Track incognito mode status
        self.history_file = "history.json"
        self.history = self.load_history()
        self.downloads = []

        # Search engines dictionary
        self.search_engines = {
            'Google': 'https://www.google.com/search?q={}',
            'Bing': 'https://www.bing.com/search?q={}',
            'DuckDuckGo': 'https://duckduckgo.com/?q={}'
        }
        self.selected_search_engine = 'Google'  # Default search engine

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        bookmark_action = QAction('Save Bookmark', self)
        bookmark_action.triggered.connect(self.save_bookmark)
        file_menu.addAction(bookmark_action)

        set_homepage_action = QAction('Set Custom Homepage', self)
        set_homepage_action.triggered.connect(self.set_custom_homepage)
        file_menu.addAction(set_homepage_action)

        download_manager_action = QAction('Download Manager', self)
        download_manager_action.triggered.connect(self.show_download_manager)
        file_menu.addAction(download_manager_action)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.back_button = QPushButton('Back')
        self.forward_button = QPushButton('Forward')
        self.reload_button = QPushButton('Reload')
        self.incognito_button = QPushButton('Incognito Mode')  # Add Incognito button
        self.history_dropdown = QComboBox()
        self.history_dropdown.addItem('History')
        self.load_history_dropdown()
        self.search_dropdown = QComboBox()  # Add search engine dropdown
        self.search_dropdown.addItem('Google')
        self.search_dropdown.addItem('Bing')
        self.search_dropdown.addItem('DuckDuckGo')

        self.new_tab_button = QPushButton('+')

        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)
        self.reload_button.clicked.connect(self.reload_page)
        self.incognito_button.clicked.connect(self.toggle_incognito_mode)  # Incognito mode toggle
        self.history_dropdown.activated[str].connect(self.load_from_history)
        self.new_tab_button.clicked.connect(self.new_tab)
        self.search_dropdown.activated[str].connect(self.update_search_engine)  # Update search engine

        self.toolbar.addWidget(self.back_button)
        self.toolbar.addWidget(self.forward_button)
        self.toolbar.addWidget(self.reload_button)
        self.toolbar.addWidget(self.incognito_button)  # Add Incognito mode button
        self.toolbar.addWidget(self.search_dropdown)  # Add search dropdown
        self.toolbar.addWidget(self.history_dropdown)
        self.toolbar.addWidget(self.new_tab_button)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.new_tab()

    def new_tab(self, url=None):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        url_bar = QLineEdit()
        url_bar.setPlaceholderText('Enter URL and press Enter...')
        url_bar.returnPressed.connect(lambda: self.load_url(browser, url_bar))
        layout.addWidget(url_bar)

        # Use a different QWebEngineProfile when in incognito mode
        browser = QWebEngineView()
        if self.incognito_mode:
            profile = QWebEngineProfile.defaultProfile().clone()
            profile.setRequestInterceptor(None)  # Disable saving of cookies and cache
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
            # If it's not a valid URL, search using the selected search engine
            search_query = url
            search_url = self.search_engines[self.selected_search_engine].format(search_query)
            browser.setUrl(QUrl(search_url))
        else:
            browser.setUrl(QUrl(url))
        if not self.incognito_mode:
            self.history.append(url)
            self.save_history()
            self.history_dropdown.addItem(url)

    def load_from_history(self, url):
        self.new_tab(url)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def save_bookmark(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        url = current_browser.url().toString()
        self.bookmarks.append(url)
        with open("bookmarks.json", "w") as file:
            json.dump(self.bookmarks, file)
        print(f'Bookmark saved: {url}')

    def go_back(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        current_browser.back()

    def go_forward(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        current_browser.reload()

    def toggle_incognito_mode(self):
        """Toggle between normal and incognito mode."""
        self.incognito_mode = not self.incognito_mode
        if self.incognito_mode:
            self.incognito_button.setText('Incognito Mode (ON)')
        else:
            self.incognito_button.setText('Incognito Mode (OFF)')
        print("Incognito Mode: ", "Enabled" if self.incognito_mode else "Disabled")

    def update_search_engine(self, engine):
        """Update the selected search engine when changed from the dropdown."""
        self.selected_search_engine = engine
        print(f'Search engine updated to: {self.selected_search_engine}')

    def save_history(self):
        """Only save history when not in incognito mode."""
        if not self.incognito_mode:
            with open(self.history_file, "w") as file:
                json.dump(self.history, file)

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                return json.load(file)
        return []

    def load_history_dropdown(self):
        for url in self.history:
            self.history_dropdown.addItem(url)

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

    def load_custom_homepage(self):
        if os.path.exists("custom_homepage.txt"):
            with open("custom_homepage.txt", "r") as file:
                return file.read().strip()
        return "https://www.google.com"

    def handle_download(self, download):
        download_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.suggestedFileName())
        if download_path:
            download.setPath(download_path)
            download.accept()
            self.downloads.append(download_path)
            print(f'Download started: {download_path}')

    def show_download_manager(self):
        self.download_window = QWidget()
        self.download_window.setWindowTitle("Download Manager")
        layout = QVBoxLayout()
        self.download_list = QListWidget()
        self.download_list.addItems(self.downloads)
        layout.addWidget(self.download_list)
        self.download_window.setLayout(layout)
        self.download_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebBrowser()
    window.show()
    sys.exit(app.exec_())
