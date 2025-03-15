# Third-party modules
from PySide6 import QtWidgets, QtGui
import sys
import os

# Local modules
from ui import MixamoDownloaderUI


def find_icon_path(icon_name):
    """Find the path to the icon file, handling both source and packaged environments."""
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


if __name__ == "__main__":
    # Create the application
    app = QtWidgets.QApplication([])
    
    # Set application metadata
    app.setApplicationName("Mixamo Downloader")
    app.setApplicationDisplayName("Mixamo Downloader")
    app.setOrganizationName("Mixamo Downloader")
    app.setOrganizationDomain("mixamodownloader.com")
    
    # Set the application icon
    icon_path = find_icon_path("mixamo.ico")
    if icon_path:
        app_icon = QtGui.QIcon(icon_path)
        app.setWindowIcon(app_icon)

    # Create and show the main window
    md = MixamoDownloaderUI()
    md.show()

    # Start the application event loop
    sys.exit(app.exec())
