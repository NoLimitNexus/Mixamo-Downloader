# Mixamo Downloader

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange?style=for-the-badge)
![Dark Mode](https://img.shields.io/badge/Dark_Mode-Enabled-black?style=for-the-badge)
![Automation](https://img.shields.io/badge/Automation-Ready-green?style=for-the-badge)

A sleek, dark-themed GUI application that automates the download process for Mixamo animations and characters. Download one animation or entire animation sets with just a few clicks!

## 🚀 Features

- **🎨 Modern Dark UI** - Easy on the eyes with a professional dark theme
- **⚡ Bulk Downloads** - Download all animations for a character at once
- **🎯 Selective Downloads** - Choose specific animations you need
- **📁 Organized Output** - Automatically organizes files by character/animation
- **⏸️ Pause/Resume** - Control downloads with pause and resume functionality
- **📊 Progress Tracking** - Real-time download progress with detailed status
- **🔧 Configurable Settings** - Customize download formats and quality

## 🎮 Perfect For

- **Game Developers** working with Unity/Unreal Engine
- **3D Animators** needing character animations
- **Indie Developers** building games on a budget
- **Students** learning game development
- **Prototype Projects** requiring quick animation assets

## 📋 Prerequisites

Before running the application:

### System Requirements
- **Python 3.7+** installed
- **Web Browser** (Chrome/Firefox recommended)
- **Active Internet Connection**
- **Mixamo Account** (free registration required)

### Required Python Packages
```bash
pip install -r requirements.txt
```

Required packages include:
- `requests` - HTTP requests handling
- `beautifulsoup4` - Web scraping
- `selenium` - Browser automation
- `tkinter` - GUI framework (usually included with Python)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/NoLimitNexus/Mixamo-Downloader.git
cd Mixamo-Downloader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup WebDriver (for Selenium)
Download ChromeDriver or GeckoDriver and ensure it's in your PATH, or place it in the project directory.

### 4. Run the Application
```bash
python mixamo_downloader.py
```

## 🎯 How to Use

### Quick Start Guide

1. **Launch the Application**
   ```bash
   python mixamo_downloader.py
   ```

2. **Login to Mixamo**
   - Enter your Mixamo credentials
   - The app will handle the login process

3. **Select Character**
   - Browse or search for your desired character
   - Preview available animations

4. **Choose Download Option**
   - **Download All**: Get every animation for the character
   - **Select Specific**: Choose individual animations
   - **Batch Download**: Queue multiple characters

5. **Configure Settings**
   - Set download format (FBX, Collada)
   - Choose animation quality
   - Select output directory

6. **Start Download**
   - Monitor progress in real-time
   - Pause/resume as needed

### Advanced Features

#### Bulk Character Downloads
```python
# Example: Download multiple characters
characters = ["Remy", "Kachujin", "Vampire"]
downloader.batch_download(characters)
```

#### Custom Format Settings
- **FBX Format**: Best for Unity/Unreal
- **Collada**: Universal format
- **Animation Quality**: 30fps standard, 60fps high quality

## 🔧 Configuration Options

### Download Settings
```json
{
  "format": "fbx",
  "fps": 30,
  "skin": true,
  "keyframe_reduction": false,
  "quality": "standard"
}
```

### Output Structure
```
downloads/
├── Character_Name/
│   ├── animations/
│   │   ├── walking.fbx
│   │   ├── running.fbx
│   │   └── jumping.fbx
│   └── character_model.fbx
```

## 🎨 GUI Features

### Dark Theme Interface
- **Professional Appearance** - Easy on the eyes
- **Intuitive Layout** - Clear navigation and controls
- **Progress Indicators** - Visual feedback for all operations
- **Status Messages** - Detailed information about current operations

### Main Interface Elements
- **Character Browser** - Preview and select characters
- **Animation List** - View available animations with thumbnails
- **Download Queue** - Manage multiple downloads
- **Settings Panel** - Configure download preferences
- **Progress Bar** - Real-time download status

## ⚠️ Important Notes

### Mixamo Terms of Service
- Ensure compliance with Mixamo's terms of service
- Use downloaded assets according to licensing agreements
- Respect rate limits to avoid account restrictions

### Performance Tips
- Close unnecessary browser windows during downloads
- Use wired internet connection for stability
- Download during off-peak hours for faster speeds

## 🐛 Troubleshooting

### Common Issues

**Login Failed**
- Verify Mixamo credentials
- Check internet connection
- Clear browser cache

**Download Errors**
- Ensure sufficient disk space
- Check file permissions
- Verify output directory exists

**Slow Downloads**
- Check internet speed
- Reduce concurrent downloads
- Choose lower quality settings

### Debug Mode
```bash
python mixamo_downloader.py --debug
```

## 🔄 Updates & Maintenance

The application includes:
- **Auto-Update Check** - Notifies of new versions
- **Error Logging** - Detailed logs for troubleshooting
- **Backup Settings** - Save and restore configurations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes and personal use. Users are responsible for complying with Mixamo's terms of service and licensing agreements.

## 🤝 Contributing

Contributions welcome! Please:
- Fork the repository
- Create a feature branch
- Submit a pull request

### Development Setup
```bash
git clone https://github.com/NoLimitNexus/Mixamo-Downloader.git
cd Mixamo-Downloader
pip install -r requirements-dev.txt
```

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Features**: Request new features via GitHub
- **Questions**: Check the FAQ or open a discussion

---

**Streamline your Mixamo workflow with professional automation!**