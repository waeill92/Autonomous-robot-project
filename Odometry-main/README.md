# logic.cpp

This file is the entry point for our robot's logic, in it are created the singletone odometry and motor controller objects, you can use them there. The `testMotor` function is exposed to `main.c` via `extern` where you can use call it to test things.

# odometry.cpp

Does the calculation for d_center, angular_velocity, linear_velocity

To get the encoder calculated x, y, theta, and d_center use `odom.getPose(out_x, out_y, out_theta, out_d_center)`

To get the angular and linear velocity, use `odom.getSpeed(out_linear_velocity, out_angular_velocity)`