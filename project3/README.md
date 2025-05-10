# Project – Game Engine and Minecraft

## Task Overview

- **3D Block World Engine:**
  - Build and navigate a voxel-style world using Python, Pygame, and OpenGL.
- **Camera and Controls:**
  - First-person camera with mouse look and WASD movement.
- **Block Interaction:**
  - Right-click to place blocks.
  - Left-click to destroy blocks with an explosion animation.

### Key Features:

- **Custom Game Engine:** Built from scratch using Pygame + PyOpenGL + PyGLM.
- **Mouse Look and WASD Movement:** Full 3D navigation experience.
- **Ray-Based Block Placement & Destruction:** Blocks are placed and destroyed based on what the player is targeting.
- **Explosion Particles:** Blocks explode into animated debris when destroyed.
- **Modular Structure:** Clean folder layout for engine, game logic, and rendering code.

---

## Running the Code

This project uses Python with OpenGL bindings. Follow the instructions below to set up a virtual environment, install dependencies, and run the game.

### 1. Create a Virtual Environment

```
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 2. Install Required Libraries

```
pip install pygame PyOpenGL PyOpenGL_accelerate PyGLM
```

> 💡 On Linux, you may also need to install system dependencies:

```
sudo apt install freeglut3 freeglut3-dev
```

### 3. Run the Game

```
python main.py
```

---

## Controls

- **WASD:** Move around
- **Mouse:** Look around
- **Left Click:** Destroy block (explodes)
- **Right Click:** Place block
- **Esc / Window Close:** Exit game

---

## Folder Structure

```
minecraft_clone/
├── engine/          # Rendering, camera, input, and block utilities
├── game/            # Game logic: world, player, explosions
├── main.py          # Game entry point
└── README.md
```

---

## Notes

- Built and tested with Python 3.10+.
- Cross-platform (Windows/Linux/Mac) as long as OpenGL is supported.
