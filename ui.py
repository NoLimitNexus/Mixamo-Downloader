# Stdlib modules
import json
import os
import sys

# Third-party modules
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

# Local modules
from downloader import HEADERS
from downloader import MixamoDownloader
from webpage import CustomWebPage


class MixamoDownloaderUI(QtWidgets.QMainWindow):
    """Main UI that allows users to bulk download animations from Mixamo.

    Users should log into their Mixamo accounts and upload the character
    they want to download animations for. This character is what Mixamo
    call the Primary Character.

    Users can choose to download all animations in Mixamo (quite slow),
    only those that contain a specific word (faster), or just the T-Pose.

    Note that only the T-Pose is downloaded with skin. Animations are
    downloaded without skin to speed things up and save space on disk.
    """
    def __init__(self):        
        """Initialize the Mixamo Downloader UI."""
        super().__init__()
        
        # Set the window title and size.
        self.setWindowTitle('Mixamo Downloader')
        self.setGeometry(100, 100, 1200, 800)
        
        # Find the icon path - handle both running from source and from PyInstaller package
        icon_path = self.find_icon_path("mixamo.ico")
        
        # Set window icon - this affects taskbar icon as well
        if icon_path:
            app_icon = QtGui.QIcon(icon_path)
            self.setWindowIcon(app_icon)
            
            # Also set the application-wide icon to ensure it appears in taskbar
            QtWidgets.QApplication.setWindowIcon(app_icon)
        
        # Apply dark theme styling
        self.apply_dark_theme()

        # Create a QWebEngineView instance (i.e: a web browser).
        self.browser = QWebEngineView()
        
        # Set size policy for the browser to expand both horizontally and vertically
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.browser.sizePolicy().hasHeightForWidth())
        self.browser.setSizePolicy(sizePolicy)

        # Create an instance of our custom QWebEnginePage.
        page = CustomWebPage()
        # Set the Mixamo website as its URL.
        page.setUrl((QtCore.QUrl('https://www.mixamo.com')))
        # Apply this page to the web browser.
        self.browser.setPage(page)
        
        # Store a reference to the page for proper cleanup
        self.web_page = page
        
        # Configure the web view to avoid scrollbars when possible
        self.browser.page().settings().setAttribute(QWebEngineSettings.ShowScrollBars, False)
        self.browser.page().settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
        # Enable smooth scrolling for a better user experience
        self.browser.page().settings().setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        # Set FocusOnNavigationEnabled to improve keyboard navigation
        self.browser.page().settings().setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        
        # The access token will be sent from the custom QWebEnginePage
        # through a signal, so we need to connect that signal to some
        # method in this class in order to get its value.
        page.retrieved_token.connect(self.apply_token)
        
        # Connect to loadFinished signal to adjust browser content once loaded
        self.browser.loadFinished.connect(self.adjust_browser_content)
        
        # Initial zoom factor - slightly smaller to ensure content fits
        self.browser.setZoomFactor(0.95)

        # Create the central widget and its layout.
        central_widget = QtWidgets.QWidget()
        central_widget.setObjectName("centralWidget")

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)  # Reduced from 10
        layout.setContentsMargins(6, 6, 6, 6)  # Reduced from 10,10,10,10

        central_widget.setLayout(layout)

        # Add the web browser to the layout with higher stretch factor
        layout.addWidget(self.browser, 10)  # Increased stretch factor from 1 to 10

        # Create a card-like container for controls
        controls_container = QtWidgets.QWidget()
        controls_container.setObjectName("controlsCard")
        controls_container.setMaximumHeight(180)  # Further reduced from 200
        controls_layout = QtWidgets.QVBoxLayout(controls_container)
        controls_layout.setSpacing(6)  # Reduced from 8
        controls_layout.setContentsMargins(8, 8, 8, 8)  # Reduced from 10,10,10,10
        layout.addWidget(controls_container, 0)  # Keep stretch factor at 0 (don't stretch)

        # Create a horizontal layout for top row (animation options and output folder)
        top_row_layout = QtWidgets.QHBoxLayout()
        top_row_layout.setSpacing(10)
        controls_layout.addLayout(top_row_layout)
        
        # Create a widget for animation options
        anim_options_widget = QtWidgets.QWidget()
        anim_opt_lyt = QtWidgets.QHBoxLayout(anim_options_widget)
        anim_opt_lyt.setSpacing(8)
        anim_opt_lyt.setContentsMargins(0, 0, 0, 0)
        
        # Create radio buttons for the different download options.
        self.rb_all = QtWidgets.QRadioButton("All animations")
        self.rb_all.setChecked(True)

        self.rb_query = QtWidgets.QRadioButton(
            "Animations containing the word:")

        self.le_query = QtWidgets.QLineEdit()
        self.le_query.setEnabled(False)
        self.le_query.setMinimumWidth(150)

        self.rb_tpose = QtWidgets.QRadioButton("T-Pose (with skin)")

        # The line edit is to be enabled only when using the query option.
        self.rb_query.toggled.connect(lambda: self.le_query.setEnabled(True))
        self.rb_all.toggled.connect(lambda: self.le_query.setEnabled(False))
        self.rb_tpose.toggled.connect(lambda: self.le_query.setEnabled(False))

        # Add the radio buttons and line edit to the download options layout.
        anim_opt_lyt.addWidget(self.rb_all)
        anim_opt_lyt.addWidget(self.rb_query)
        anim_opt_lyt.addWidget(self.le_query)
        anim_opt_lyt.addWidget(self.rb_tpose)
        anim_opt_lyt.addStretch()

        # Add animation options to top row layout
        top_row_layout.addWidget(anim_options_widget)

        # Create a group box where users can chose the output folder.
        gbox_output = QtWidgets.QGroupBox("Output Folder")
        gbox_output.setMaximumHeight(65)
        gbox_output.setMinimumWidth(300)

        gbox_output_lyt = QtWidgets.QHBoxLayout()
        gbox_output_lyt.setContentsMargins(8, 12, 8, 8)
        gbox_output.setLayout(gbox_output_lyt)

        # Create the content of the group box.
        self.le_path = QtWidgets.QLineEdit()
        self.le_path.setPlaceholderText("Select output folder...")
        tb_path = QtWidgets.QToolButton()

        icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_DirIcon)

        tb_path.setIcon(icon)
        tb_path.setMinimumSize(26, 26)

        # When the tool button is clicked, launch a QFileDialog.
        tb_path.clicked.connect(self.set_path)

        # Add the line edit and tool button to the group box layout.
        gbox_output_lyt.addWidget(self.le_path)
        gbox_output_lyt.addWidget(tb_path)

        # Add the group box to the top row layout
        top_row_layout.addWidget(gbox_output)

        # Create a horizontal layout for buttons and progress
        action_layout = QtWidgets.QHBoxLayout()
        action_layout.setSpacing(10)
        controls_layout.addLayout(action_layout)

        # Create the button that will launch the download process.
        self.get_btn = QtWidgets.QPushButton('Start Download')
        self.get_btn.clicked.connect(self.get_access_token)
        self.get_btn.setMinimumHeight(38)
        self.get_btn.setMinimumWidth(150)
        self.get_btn.setObjectName("primaryButton")

        # Create the progress bar.
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFormat(f"Downloading %v/%m")
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setMinimumHeight(22)
        
        # Create a button to stop the download.
        # It will be disabled by default, and enabled only when downloading.
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_download)  
        self.stop_btn.setMinimumHeight(38)
        self.stop_btn.setFixedWidth(80)
        self.stop_btn.setObjectName("stopButton")
        
        # Add the buttons and progress bar to layout
        action_layout.addWidget(self.get_btn)
        action_layout.addWidget(self.progress_bar, 1)
        action_layout.addWidget(self.stop_btn)
        
        # Set this widget as the central one for the Main Window.
        self.setCentralWidget(central_widget)

    def apply_dark_theme(self):
        """Apply dark theme styling to the application"""
        # Set the application style to Fusion which works well with custom styling
        QtWidgets.QApplication.setStyle("Fusion")
        
        # Define the dark theme color palette
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(45, 45, 48))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(30, 30, 30))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(0, 120, 215))
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(0, 120, 215))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
        
        # Apply the dark palette to the application
        QtWidgets.QApplication.setPalette(dark_palette)
        
        # Apply stylesheet for more detailed styling
        style_sheet = """
        QMainWindow {
            background-color: #1E1E1E;
        }
        QWidget {
            color: #FFFFFF;
        }
        QWidget#centralWidget {
            background-color: #1E1E1E;
        }
        QWidget#controlsCard {
            background-color: #252526;
            border-radius: 6px;
            border: 1px solid #3F3F46;
        }
        QGroupBox {
            border: 1px solid #3F3F46;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: bold;
            padding: 6px;
            background-color: #2D2D30;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
            color: #CCCCCC;
            font-size: 11px;
        }
        QPushButton {
            background-color: #2D2D30;
            color: white;
            border: 1px solid #3F3F46;
            border-radius: 3px;
            padding: 4px 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #3E3E40;
            border: 1px solid #007ACC;
        }
        QPushButton:pressed {
            background-color: #1E1E1E;
        }
        QPushButton:disabled {
            background-color: #2D2D30;
            color: #656565;
            border: 1px solid #3F3F46;
        }
        QPushButton#primaryButton {
            background-color: #0078D4;
            color: white;
            border: none;
            border-radius: 3px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton#primaryButton:hover {
            background-color: #106EBE;
        }
        QPushButton#primaryButton:pressed {
            background-color: #005A9E;
        }
        QPushButton#stopButton {
            background-color: #E81123;
            color: white;
            border: none;
            font-size: 11px;
        }
        QPushButton#stopButton:hover {
            background-color: #F1707A;
        }
        QPushButton#stopButton:pressed {
            background-color: #D13438;
        }
        QPushButton#stopButton:disabled {
            background-color: #2D2D30;
            color: #656565;
        }
        QLineEdit {
            border: 1px solid #3F3F46;
            border-radius: 3px;
            padding: 4px;
            background-color: #1E1E1E;
            color: #FFFFFF;
            selection-background-color: #007ACC;
        }
        QLineEdit:focus {
            border: 1px solid #007ACC;
        }
        QRadioButton {
            spacing: 6px;
            color: #CCCCCC;
            font-size: 11px;
        }
        QRadioButton:hover {
            color: #FFFFFF;
        }
        QRadioButton::indicator {
            width: 14px;
            height: 14px;
            border-radius: 7px;
        }
        QRadioButton::indicator:checked {
            background-color: #007ACC;
            border: 2px solid #FFFFFF;
        }
        QRadioButton::indicator:unchecked {
            background-color: #1E1E1E;
            border: 2px solid #CCCCCC;
        }
        QProgressBar {
            border: 1px solid #3F3F46;
            border-radius: 3px;
            text-align: center;
            background-color: #1E1E1E;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 11px;
        }
        QProgressBar::chunk {
            background-color: #007ACC;
            border-radius: 2px;
        }
        QToolButton {
            background-color: #007ACC;
            border: none;
            border-radius: 3px;
        }
        QToolButton:hover {
            background-color: #106EBE;
        }
        QToolButton:pressed {
            background-color: #005A9E;
        }
        /* WebEngineView customization */
        QWebEngineView {
            border: 1px solid #3F3F46;
            border-radius: 3px;
        }
        """
        
        self.setStyleSheet(style_sheet)

    def get_access_token(self):
        """Enter a JavaScript command to retrieve the Mixamo access token.

        The javaScriptConsoleMessage method from QWebEnginePage will catch
        every message printed to the browser's console.

        In this case, we're printing to the console the 'access_token' used
        by Mixamo, so that the javaScriptConsoleMessage can catch it and
        return that value to us.
        """

        script = """
        var token = localStorage.getItem('access_token');
        console.log('ACCESS TOKEN:', token);
        """
        
        # Run the JavaScript code on our page.
        self.browser.page().runJavaScript(script)

    def apply_token(self, token):
        """Add the access token to the HTTP Request Headers.

        This method is invoked as soon as the access token is sent through
        the QWebEnginePage signal, so we'll use it to launch the downloader
        as well.

        :param token: Mixamo Access Token
        :type token: str
        """
        HEADERS["Authorization"] = f"Bearer {token}"
        self.run_downloader()

    def run_downloader(self):
        """Wrapper method that sets everything up for the download.

        The download is run on a separate thread to prevent the UI from
        freezing. This also allows the progress bar to the updated on
        every download, giving the user an appropriate experience.
        """
        # Create a QThread instance.
        self.thread = QtCore.QThread()

        # Get the download mode, query (if any) and the output folder path.
        mode = self.get_mode()
        query = self.le_query.text()
        path = self.le_path.text()

        # Create a MixamoDownloader instance and move it to the new thread.
        self.worker = MixamoDownloader(path, mode, query)
        self.worker.moveToThread(self.thread)

        # As soon as the thread is started, the run method on the worker
        # will be invoked so that it starts processing everything.
        self.thread.started.connect(self.worker.run)
        # The 'Stop' button will also be enabled when the thread is started.
        self.thread.started.connect(self.stop_btn.setEnabled(True))
        # The 'Download' button will be disabled.
        self.thread.started.connect(self.get_btn.setEnabled(False))

        # When the worker emits the finished signal, close the thread.
        self.worker.finished.connect(self.thread.quit)
        # Set the worker to be deleted after all pending events are done.
        self.worker.finished.connect(self.worker.deleteLater)
        # Same with the thread when it is closed.
        self.thread.finished.connect(self.thread.deleteLater)
        # Once the thread is closed, restore buttons to its default state.
        self.thread.finished.connect(lambda: self.stop_btn.setEnabled(False))
        self.thread.finished.connect(lambda: self.get_btn.setEnabled(True))

        # Read signals from the worker that allows us to set the progress bar.
        # The 'total_tasks' signal emits the amount of items to be downloaded.
        # The 'current_task' signal emits whenever an item has been downloaded.
        self.worker.total_tasks.connect(self.set_progress_bar)
        self.worker.current_task.connect(self.update_progress_bar)

        # Start the thread.
        self.thread.start()

    def set_progress_bar(self, total_tasks):
        """Set the progress bar range to the proper values.

        The 'total_tasks' signal from the QWebEnginePage emits the amount of
        animations to be downloaded. This number is what we catch with this
        method in order to set the progress bar.
        """
        # Reset the progress bar.
        self.progress_bar.reset()
        # Set the progress bar range to the proper values.
        # If we're downloading just one animation, the range will be [0, 1].
        self.progress_bar.setRange(0, total_tasks)

    def update_progress_bar(self, step):
        """Update the progress bar value.

        The 'current_task' signal from the QWebEnginePage emits every time
        an animation has been downloaded, so we'll use that value to update
        the progress bar.
        """
        self.progress_bar.setValue(step)

    def stop_download(self):
        """Send a flag to the worker to let him know that it should stop.

        Note that once the flag is sent, the code will wait for the current
        download to finish before the thread is closed.
        """
        self.worker.stop = True

    def set_path(self):
        """Ask the user to select the output folder through a QFileDialog."""
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select the output folder')
        
        # If a folder has been selected by the user, update the line edit.
        if path:
            self.le_path.setText(path)

    def get_mode(self):
        """Read the radio buttons to know which download mode to be used.

        :return: Download mode
        :rtype: str
        """
        if self.rb_all.isChecked():
            return "all"
        elif self.rb_query.isChecked():
            return "query"
        elif self.rb_tpose.isChecked():
            return "tpose"

    def closeEvent(self, event):
        """Handle window close event to properly clean up resources."""
        # Delete the web page explicitly to avoid warnings about unreleased profiles
        if hasattr(self, 'browser') and self.browser:
            self.browser.setPage(None)
            
        if hasattr(self, 'web_page') and self.web_page:
            self.web_page.deleteLater()
            
        # Accept the close event
        event.accept()
        
    def resizeEvent(self, event):
        """Handle window resize events to adjust content scaling."""
        super().resizeEvent(event)
        self.adjust_browser_content()
        
    def adjust_browser_content(self):
        """Adjust browser content to fit the window without scrollbars."""
        # Run JavaScript to adjust the page content to fit without scrollbars
        script = """
        // Set body overflow to hidden to avoid scrollbars
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
        
        // Make sure the content fills the available space
        document.documentElement.style.height = '100%';
        document.body.style.height = '100%';
        document.body.style.margin = '0';
        document.body.style.padding = '0';
        
        // Remove any fixed width constraints
        document.documentElement.style.minWidth = 'auto';
        document.body.style.minWidth = 'auto';
        
        // Adjust content to fit view
        var viewportHeight = window.innerHeight;
        var viewportWidth = window.innerWidth;
        
        // Ensure Mixamo content scales correctly within the viewport
        var mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.height = viewportHeight + 'px';
            mainContent.style.overflow = 'hidden';
        }
        
        // Additional adjustments for Mixamo-specific elements if needed
        var viewportElements = document.querySelectorAll('.viewport, .wrapper, .container');
        for (var i = 0; i < viewportElements.length; i++) {
            viewportElements[i].style.height = '100%';
            viewportElements[i].style.overflow = 'hidden';
            viewportElements[i].style.maxWidth = '100%';
        }
        
        // Adjust any fixed-width containers
        var fixedWidthElements = document.querySelectorAll('[style*="width"]');
        for (var i = 0; i < fixedWidthElements.length; i++) {
            // Only modify elements with explicit pixel widths
            if (fixedWidthElements[i].style.width && fixedWidthElements[i].style.width.includes('px')) {
                fixedWidthElements[i].style.maxWidth = '100%';
                fixedWidthElements[i].style.width = 'auto';
            }
        }
        """
        
        # Run the JavaScript code on our page
        self.browser.page().runJavaScript(script)

    def find_icon_path(self, icon_name):
        """Find the path to the icon file, handling both source and packaged environments.
        
        :param icon_name: Name of the icon file to find
        :type icon_name: str
        :return: Path to the icon file or None if not found
        :rtype: str or None
        """
        # Check if running from frozen executable (PyInstaller package)
        if getattr(sys, 'frozen', False):
            # Try to find the icon in several possible locations
            base_path = os.path.dirname(sys.executable)
            
            # Check in the same directory as the executable
            icon_path = os.path.join(base_path, icon_name)
            if os.path.exists(icon_path):
                return icon_path
                
            # Check in _internal directory (PyInstaller typical location)
            icon_path = os.path.join(base_path, '_internal', icon_name)
            if os.path.exists(icon_path):
                return icon_path
                
            # Check one directory up (distribution folder structure)
            icon_path = os.path.join(os.path.dirname(base_path), icon_name)
            if os.path.exists(icon_path):
                return icon_path
        else:
            # Running from source
            # Check current directory
            if os.path.exists(icon_name):
                return icon_name
                
            # Check script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, icon_name)
            if os.path.exists(icon_path):
                return icon_path
        
        # Return None if icon not found
        return None
