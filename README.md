# Ray Tracing Example

This project is a **minimal** ray tracer written in C++. It renders three colored spheres (red, green, and blue) against a white background, outputting the image data in [PPM](http://netpbm.sourceforge.net/doc/ppm.html) format to standard output.


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