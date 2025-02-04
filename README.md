# Ray Tracing

This project is a **minimal** ray tracer written in Python. It renders three colored spheres (red, green, and blue) against a white background, outputting the image data in [PPM](http://netpbm.sourceforge.net/doc/ppm.html) format to standard output.


## Features

- Defines spheres in 3D space and computes their intersection with a viewing ray.
- Renders each pixel by casting a ray and returning the color of the nearest sphere (or white if no sphere is hit).
- Outputs the final image as PPM data, which can be redirected to an image file (e.g., `image.ppm`).

---

## Requirements

- A **C++ compiler** that supports **C++11** or higher:
  - On macOS, `clang++` is available by default via Xcode Command Line Tools.
  - On Linux, you can typically install or use `g++` or `clang++`.
  - On Windows, you can use [Visual Studio](https://visualstudio.microsoft.com/downloads/), [MSYS2/MinGW](https://www.msys2.org/), or [Cygwin](https://www.cygwin.com/).

- **No external libraries** are needed; everything is done via the C++ standard library.

## Usage
Start by cloning this repository using

```bash
git clone https://github.com/haidar1337/basic-ray-tracer.git
```

cd into the project directory using

```bash
cd path/to/cloned_repository
```

Compile the program to a binary executable using your compiler
- Using g++, you can use the following
```bash
g++ main.cc -o raytrace
```
- Using clang, you can use the following
```bash
clang++ main.cc -o raytrace
```
- Using gcc, you can use the following
```bash
gcc main.cc -o raytrace
```
Once you compile the program, execute it and redirect the execution to an image.ppm file like so
```bash
./raytrace > image.ppm
```

## Viewing the Output
Your program will print a PPM (ASCII “P3” variant) to stdout.

- On macOS: ```open image.ppm```
- On Linux: ```xdg-open image.ppm``` or ```eog image.ppm```
- On Windows:
Some apps/viewers may read ```.ppm``` files directly (e.g., IrfanView, XnView, GIMP).
Alternatively, convert it to PNG or JPG with an image conversion tool.
Once opened, you should see three colored spheres on a white background.

