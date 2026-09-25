# 8-Ball Pool 3D 🎱

**8-Ball Pool 3D** is a high-performance Python billiards simulation using Pygame and Pymunk. It features strict BCA rules, a regulation 2:1 table, dynamic raycast aiming, and advanced cue ball spin. Custom asset caching ensures a flawless 60 FPS experience on high-res displays, all packaged into a single click-to-play executable.


## ✨ Features

* **Tournament-Grade Physics:** Powered by the Pymunk rigid-body engine. Includes authentic ball friction, dynamic swerve forces, and comprehensive cue ball spin control (English, Follow, Draw).
* **Strict BCA Rule Enforcement:** Fully functional game state manager that handles solids/stripes assignment, first-hit validation, scratch penalties, early 8-ball loss conditions, and the official "No Rail" foul.
* **Precision Aiming System:** Dynamic raycast aiming line that accurately reflects off physical cushions while intelligently phasing through pocket sensors.
* **Regulation Geometry:** Mathematically locked 2:1 table ratio (1200x600 play area) with uniform 140-pixel pocket openings across both corner and side pockets.
* **Hyper-Optimized Rendering:** Utilizes a static background pre-rendering cache and rotational image caching to eliminate CPU bottlenecks, guaranteeing a buttery-smooth 60 FPS even on 4K Retina displays.
* **Clean UI/UX:** Features a dedicated top-bar safe zone, dynamic "Ball In Hand" indicators, interactive pause/win screens, and a precision spin-adjustment overlay.

## 🎮 How to Play (No Installation Required)

You do not need Python installed to play this game. Standalone executables are automatically compiled for Windows and macOS.

1. Navigate to the **[Releases](../../releases)** page on this repository.
2. Download the latest version for your operating system:
   * **Windows:** Download and run `8-Ball-Pool-Windows.exe`.
   * **macOS:** Download and extract `8-Ball-Pool-macOS.zip`, then open the application.
3. Enter player names, break the rack, and enjoy!

## 🕹️ Controls

* **Mouse Movement:** Aim the cue stick.
* **Left Click & Hold (Near Cue Ball):** Drag the cue ball when "Ball In Hand" is active.
* **Left Click & Drag (Away from Cue Ball):** Pull back to charge your shot power. Release to strike.
* **Spin Button (Top Left):** Click to open the precision spin overlay and adjust your strike point on the cue ball.
* **ESC Key:** Pause or resume the game.

## 🛠️ Tech Stack

* **Language:** Python 3.11
* **Rendering & UI:** Pygame (Custom hardware scaling, double buffering)
* **Physics Engine:** Pymunk 7.0+ (2D rigid-body dynamics, shape filtering, collision callbacks)
* **CI/CD:** GitHub Actions (Automated multi-OS executable builds via PyInstaller)

## 💻 Local Development

If you want to run the game from the source code or contribute:

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/8ballpool3D.git](https://github.com/yourusername/8ballpool3D.git)
   cd 8ballpool3D
