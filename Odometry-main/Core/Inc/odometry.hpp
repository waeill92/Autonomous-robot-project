#ifndef ODOMETRY_HPP
#define ODOMETRY_HPP

#include "main.h"

class Odometry {
public:
    Odometry(TIM_HandleTypeDef* htim_left, TIM_HandleTypeDef* htim_right);

    void update(float dt);
//    void handleInterrupt();
    void getSpeed(float &out_linear_velocity, float &out_angular_velocity) const;
    void getPose(float &out_x, float &out_y, float &out_theta, float &out_d_center) const;

private:
    TIM_HandleTypeDef* htim_left;
    TIM_HandleTypeDef* htim_right;

    int32_t last_left;
    int32_t last_right;

    float left_distance;
    float right_distance;
    float distance;

    float x;
    float y;
    float theta;

    float linear_velocity;
    float angular_velocity;

    uint32_t last_update_ms;

    static const int MA_SIZE = 20;
    float ma_linear[MA_SIZE];
    float ma_angular[MA_SIZE];
    int ma_idx;
    int ma_count;
};

#endif
