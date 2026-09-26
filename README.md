# Dali² – Autonomous Robot (RoboCup ENSI 2025)

Firmware and vision-pipeline code for **Dali²**, an autonomous robot built for the **8th edition of RoboCup ENSI** (October 19, 2025), on the theme *"Glitched Universe: Chasing Reality"*.

The robot combined a 3D-printed chassis and obstacle-manipulation arm, an STM32-based navigation/control stack (odometry, IMU, motor + encoder control), and a Raspberry Pi vision pipeline (YOLOv8 object detection + a custom tiny CNN for digit recognition) communicating over UART. A random fault in the electronics prevented the robot from competing on the day, but the full system — mechanics, embedded control, and AI vision — was built, tested, and integrated.

## Repository Structure

This repository aggregates the different subsystems of the robot, each originally developed as its own module:

```
Odometry-main/           # STM32 — wheel-encoder based odometry
IMU-main/                 # STM32 — BNO055 IMU (orientation, gyro, acceleration)
encoder_and_motor-main/   # STM32 — PWM motor control + quadrature encoders
Object_detection-main/    # Raspberry Pi — YOLOv8 vision pipeline + UART link
```

> **Note on model files:** the `Object_detection-main/Models/` folder originally contained several exported/trained YOLO weight variants (`.pt`, OpenVINO, NCNN, INT8-quantized) that made this repo ~400 MB. The less essential exports were removed to keep the repo lightweight — the retained files are enough to show the model formats and export pipeline used.

## Mechanical

- Chassis and obstacle-manipulation arm modeled in **SolidWorks** and 3D-printed in **PLA**.

## Embedded / Navigation (STM32)

Three STM32CubeIDE projects, each targeting a specific piece of the navigation stack:

### `encoder_and_motor-main`
Low-level motor control: configures a PWM timer (`TIM1`) to drive the motors and two quadrature-encoder timers (`TIM2`, `TIM5`) to read wheel rotation, with a basic speed ramp-up routine in the main loop.

### `Odometry-main`
Builds on the same quadrature-encoder timer setup (`TIM2`, `TIM5` in encoder mode) as a base for computing the robot's position/heading (odometry) to feed into navigation — intended to interface with **ROS** on the higher-level side.

### `IMU-main`
Driver and application code for the **Bosch BNO055** 9-DOF orientation sensor over I²C (custom `bno055.c`/`bno055_stm32` driver). Configures the sensor in **NDOF fusion mode** and reads gyroscope, linear acceleration, and Euler-angle orientation vectors, printed over UART for debugging.

All three are STM32CubeIDE/CubeMX-generated projects (STM32F4 / STM32L4 targets) — open the relevant folder directly in STM32CubeIDE to build and flash.

## Vision & AI (Raspberry Pi)

`Object_detection-main/Run/main.py` is the main vision service: it loads a **YOLOv8 object-detection model** (cubes/pyramids) and a **digit-recognition model** (custom tiny CNN, trained to recognize the digits **3, 5, 6, 9**), listens for commands over a UART link from the STM32, and replies with the detection result:

- `"digit"` → runs digit recognition on the current camera frame, returns the most confident digit
- `"object"` → runs object detection, returns a `"<pyramid_count> <cube_count>"` string
- `"color"` → runs HSV-based color detection (`RBG.py`) for red/green/blue targets

Supporting scripts:
- `Data_set_utils/` — dataset generation, shuffling, and labeling utilities used to build the training sets for both models
- `Models/export.py`, `Models/format.py` — export trained YOLO weights to OpenVINO / NCNN / INT8-quantized formats for faster inference on the Raspberry Pi
- `UART/` — standalone send/receive scripts used to test the serial link between the Pi and the STM32 independently of the full pipeline

## Tech Stack

| Layer | Tools |
|---|---|
| Mechanical | SolidWorks, 3D printing (PLA) |
| Embedded / Navigation | STM32 (HAL), C, quadrature encoders, PWM, I²C, ROS (odometry integration) |
| PCB | Custom PCB, ferric chloride etching |
| Vision / AI | Raspberry Pi, Python, OpenCV, Ultralytics YOLOv8, custom tiny CNN |
| Comms | UART (STM32 ↔ Raspberry Pi) |

## Team

Built for RoboCup ENSI 2025 by:
- Wael Chaabi
- Mohamed Ali Maatoug
- Mohamed Ali Elhamdi
- Mohamed Rayen Kamel

With thanks to **Association Robotique ENSI** for the opportunity.
