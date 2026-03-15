#pragma once
#include "stm32f4xx_hal.h"
#include "odometry.hpp"
#include "pid.hpp"

class MotorController {
public:
    MotorController(TIM_HandleTypeDef* htim_left,
                    uint32_t channel_left,
                    GPIO_TypeDef* dir1_left_port, uint16_t dir1_left_pin,
                    GPIO_TypeDef* dir2_left_port, uint16_t dir2_left_pin,
                    TIM_HandleTypeDef* htim_right,
                    uint32_t channel_right,
                    GPIO_TypeDef* dir1_right_port, uint16_t dir1_right_pin,
                    GPIO_TypeDef* dir2_right_port, uint16_t dir2_right_pin,
                    Odometry* odom);

    void setSpeed(float left_speed, float right_speed); // -1.0 .. 1.0
    void stop();                                       // Stop both motors
    void moveDistance(float distance_cm); // Blocking move
    void moveAngle(float angle_deg);

private:
    PID pid_linear_vel;
    PID pid_pos;
    PID pid_angle;
    PID pid_angular_vel;

private:
    TIM_HandleTypeDef* htim_left;
    uint32_t channel_left;
    GPIO_TypeDef* dir1_left_port;
    uint16_t dir1_left_pin;
    GPIO_TypeDef* dir2_left_port;
    uint16_t dir2_left_pin;

    TIM_HandleTypeDef* htim_right;
    uint32_t channel_right;
    GPIO_TypeDef* dir1_right_port;
    uint16_t dir1_right_pin;
    GPIO_TypeDef* dir2_right_port;
    uint16_t dir2_right_pin;

    Odometry* odom;
};
