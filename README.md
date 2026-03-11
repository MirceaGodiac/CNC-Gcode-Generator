![Video Project 1](https://github.com/user-attachments/assets/f24439f1-4350-40fb-a7f0-617c8ad8b3de)

# 0.1mm Precision CNC Gantry: Image to Boustrophedon Toolpath

This repository contains the software and firmware pipeline for a custom-built, 0.1mm precision CNC drawing gantry. It converts standard digital images into a single, continuous, amplitude-modulated toolpath optimized for 8-bit microcontrollers.



## System Architecture

The project is split into two distinct environments to handle the computational load and real-time hardware constraints:

1. **The Python/OpenCV Pipeline (Host):** Maps image pixel brightness into a 50,000-point matrix. [cite_start]It generates a 194x258 grid representing 11 discrete intervals (0-10) of "squiggle" intensity, outputting a highly optimized G-code command chain[cite: 15, 16].
2. [cite_start]**The C++ Arduino Firmware (Client):** A custom G-code parser running on an Arduino Uno that handles the complex trigonometry of motor micro-stepping[cite: 17]. 

## Solving the Hardware Bottleneck: The 1KB Buffer




Passing 50,000 continuous shading commands directly over Serial or standard SPI reads causes severe motor jitter due to the Arduino's limited SRAM and variable SD card read speeds. 

[cite_start]To solve this, the C++ firmware implements a **1KB circular instruction buffer**[cite: 18]. 
* The Python script compiles the high-level toolpath into compact `G1 X[pos] Y[pos] S[intensity]` commands.
* The SD card asynchronously fills the buffer while the Arduino executes the micro-steps.
* [cite_start]**Result:** Zero motor stalling and highly accurate image reproduction without dropping steps[cite: 18].

## How to Run the Toolpath Generator

```bash
# Install requirements
pip install opencv-python numpy

# Run the matrix generator
python generate_toolpath.py
