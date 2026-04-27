# 🤲 Gesture Calculator

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A revolutionary **gesture-controlled calculator** that uses your webcam to detect hand gestures and perform real-time arithmetic calculations. No keyboard, no mouse - just your hands!

## 🎯 What Makes This Special

Transform your laptop into a futuristic calculator using nothing but hand gestures. This isn't just a calculator - it's a glimpse into the future of human-computer interaction.

## ✨ Features

🤲 **Gesture Recognition**
- Numbers 0-10 using finger counting (right hand 1-5, left hand 6-10)
- Mathematical operators through intuitive hand gestures
- Real-time hand tracking with 21-point landmark detection

⏱️ **Smart Confirmation System**
- 2-second hold confirmation prevents accidental inputs
- Visual progress bar shows confirmation status
- Instant visual feedback with border color changes

🎨 **Intuitive UI**
- Live equation building display
- Current state and gesture indicators
- Error handling with clear messages
- Professional on-screen interface

🛡️ **Robust Error Handling**
- Division by zero protection
- Webcam access validation
- Graceful recovery from all error states

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/nevil06/PyMath-.git
cd PyMath-

# Install dependencies
pip install opencv-python mediapipe

# Run the calculator
python final_gesture_calculator.py
```

### System Requirements
- Python 3.7+
- Webcam access
- Windows, macOS, or Linux

## 🎮 How to Use

### Numbers (0-5)
- **Right Hand**: Show 0-5 fingers and hold for 1 second
- **Keyboard Backup**: Press 0-5 keys for instant input

### Operators
| Gesture | Method | Operation |
|---------|--------|-----------|
| 🖱️ **Mouse Click** | Click buttons on right side | Addition (+) |
| �️ **Mouse Click** | Click buttons on right side | Subtraction (−) |
| 🖱️ **Mouse Click** | Click buttons on right side | Multiplication (×) |
| 🖱️ **Mouse Click** | Click buttons on right side | Division (÷) |

### Special Commands
- **Reset**: Press 'R' key to clear everything
- **Quit**: Press 'Q' key to exit application

### Workflow
1. **Show first number** → Hold RIGHT hand with 0-5 fingers for 1 second → ✅ Confirmed
2. **Select operator** → Click operator button (+, −, ×, ÷) on right side → ✅ Confirmed  
3. **Show second number** → Hold RIGHT hand with 0-5 fingers for 1 second → ✅ Confirmed
4. **Auto-calculate** → Result displays automatically
5. **Auto-reset** → Clears after 2 seconds, ready for next calculation

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Computer Vision** | OpenCV | Webcam capture & UI rendering |
| **Hand Detection** | MediaPipe Tasks API | Real-time hand landmark detection |
| **Gesture Recognition** | Custom Algorithm | Finger counting and gesture classification |
| **State Management** | Python | Clean state machine implementation |

## 📂 Project Structure

```
PyMath-/
├── final_gesture_calculator.py    # Main working application
├── hand_landmarker.task          # MediaPipe hand detection model
├── main.py                       # Legacy file (original gesture calculator)
├── README.md                     # This file
└── LICENSE                       # MIT License
```

## 🎯 Use Cases

- **Education**: Interactive math learning for students
- **Accessibility**: Hands-free calculator for users with mobility limitations  
- **Presentations**: Impressive demo of computer vision capabilities
- **Research**: Base for gesture recognition and HCI projects
- **Fun**: Futuristic calculator experience for everyone

## 🔧 Technical Details

### State Machine
The application uses a clean finite state machine:
- `ENTER_FIRST_NUMBER` → `SELECT_OPERATOR` → `ENTER_SECOND_NUMBER` → `SHOW_RESULT` → `RESET`

### Gesture Detection Algorithm
1. **Hand Landmark Detection**: 21 points per hand using MediaPipe
2. **Finger Counting**: Compare tip vs. PIP joint positions
3. **Gesture Classification**: Pattern matching on finger combinations
4. **Confirmation System**: 2-second hold timer with visual feedback

### Error Handling
- Division by zero → Clear error message + auto-reset
- No webcam → Graceful exit with helpful message
- No hands detected → User guidance prompt
- Invalid gestures → Ignored with visual feedback

## 🔮 Future Enhancements

- � **Mobile App Version**: iOS/Android compatibility
- 🧮 **Advanced Operations**: Square root, power, trigonometry
- 🎯 **Gesture Customization**: User-defined gesture mappings
- 📊 **Calculation History**: Save and review past calculations
- 🌐 **Web Interface**: Browser-based version
- 🎨 **Themes**: Customizable UI themes and colors

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Commit** your changes: `git commit -m "Add amazing feature"`
4. **Push** to the branch: `git push origin feature-name`
5. **Submit** a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/PyMath-.git
cd PyMath-

# Install development dependencies
pip install opencv-python mediapipe cvzone

# Run tests (if you add them)
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Nevil Anson Dsouza**
- GitHub: [@nevil06](https://github.com/nevil06)
- Project: [PyMath-](https://github.com/nevil06/PyMath-)

## 🙏 Acknowledgments

- **MediaPipe** team for excellent hand tracking
- **OpenCV** community for computer vision tools
- **cvzone** for simplified gesture recognition

## ⭐ Support

If you find this project useful:
- Give it a ⭐ on GitHub
- Share it with friends and colleagues
- Consider contributing to make it even better!

---

**Ready to calculate with your hands? Install and run the gesture calculator now!** 🚀
