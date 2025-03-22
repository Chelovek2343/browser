# Custom Web Browser

## Overview
This is a custom web browser built using **PyQt5** and **Qt WebEngine**, providing essential browsing features along with additional functionality like **Incognito Mode, Custom Search Engines, Dark Mode, and a Download Manager**.

## Features
- **Tabbed Browsing**: Open multiple websites in different tabs.
- **Back, Forward, Reload Navigation**: Standard navigation buttons.
- **Custom Homepage**: Set a preferred homepage.
- **Bookmarks**: Save frequently visited websites.
- **Download Manager**: Track and manage downloads.
- **Incognito Mode**: Private browsing that does not save history.
- **Dark Mode**: Toggle between light and dark themes.
- **Custom Search Engine**: Choose between Google, Bing, and DuckDuckGo.
- **History Management**: View and load previously visited sites.

## Installation
### Prerequisites
Ensure you have **Python 3.x** installed on your system.

### Install Dependencies
```sh
pip install PyQt5 PyQtWebEngine speechrecognition pyaudio
```

### Run the Browser
```sh
python main.py
```

## Usage
1. **Navigation**: Use the back, forward, and reload buttons for easy browsing, ctrl + 1 and etc.
2. **New Tab**: Click the `+` button to open a new tab.
3. **Search or Enter URL**: Type in the address bar and press Enter.
4. **Bookmarks**: Click `File > Save Bookmark` to save the current page.
5. **Download Files**: Click links to download, and track progress in the Download Manager.
7. **Incognito Mode**: Activate private browsing mode via the toolbar button.
8. **Change Search Engine**: Use the dropdown to switch between Google, Bing, and DuckDuckGo.
9. **Closing Tabs**: Ctrl + W and Ctlr + T
10. **Voice Recognition**

## File Structure
```
/
│── main.py              # Main application script
│── history.json         # Stores browsing history
│── bookmarks.json       # Stores saved bookmarks
│── README.md            # Project documentation
```

## Future Improvements
- Support for browser extensions.
- Advanced history management.
- Customizable themes.
- More search engine options.

## License
This project is licensed under the MIT License.

## Contributors
- **[Ulugbekov Almzabek]** – Project Manager
- **[Talantbekov Tilek]** – Ux Ui desinger
- **[Sultanov Temirlan]** – Backend Developer
- **[Osmonov Ulugbek]** – Frontend Developer

---
### Happy Browsing! 🚀

