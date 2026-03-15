#include "odometry.hpp"
#include <cmath>

#define PI 3.1415926535f
#define WHEEL_DIAMETER_CM 6.64f
#define WHEEL_CIRCUMFERENCE_CM (WHEEL_DIAMETER_CM * PI)
#define TICKS_PER_REVOLUTION 1775.0f
#define DISTANCE_PER_TICK_CM (WHEEL_CIRCUMFERENCE_CM / TICKS_PER_REVOLUTION)
#define WHEEL_BASE_CM 26.7f //23.7f
#define MA_SIZE 20

Odometry::Odometry(TIM_HandleTypeDef* htim_left, TIM_HandleTypeDef* htim_right)
    : htim_left(htim_left), htim_right(htim_right),
      last_left(0), last_right(0),
      left_distance(0), right_distance(0), distance(0),
      linear_velocity(0), angular_velocity(0),
      x(0), y(0), theta(0), last_update_ms(0),
      ma_idx(0), ma_count(0)
{
    for (int i = 0; i < MA_SIZE; i++) {
        ma_linear[i] = 0.0f;
        ma_angular[i] = 0.0f;
    }
}

float dbg_dl = 0;
float dbg_dr = 0;
float dbg_center = 0;
float dbg_theta = 0;
float idx = 0;
float dbg_linear = 0;
float dbg_angular = 0;
float dbg_dt = 0;
float dbg_left = 0;
float dbg_right = 0;
float dbg_last_left = 0;
float dbg_x=0;
float dbg_y=0;
void Odometry::update(float dt) {
    if (dt <= 0.0f) dt = 1e-3f;

    int32_t left = __HAL_TIM_GET_COUNTER(htim_left);
    int32_t right = __HAL_TIM_GET_COUNTER(htim_right);
    dbg_left=left;
    dbg_right=right;

    dbg_last_left=last_left;

    int32_t d_left = left - last_left;
    int32_t d_right = right - last_right;

    last_left = left;
    last_right = right;

    float dl = d_left * DISTANCE_PER_TICK_CM;
    float dr = d_right * DISTANCE_PER_TICK_CM;

    left_distance  += dl;
    right_distance += dr;

    float d_center = (dl + dr) / 2.0f;
    distance += d_center;
    float d_theta = (dr - dl) / WHEEL_BASE_CM;

    x += d_center * std::cos(theta + d_theta / 2.0f);
    y += d_center * std::sin(theta + d_theta / 2.0f);
    dbg_x=x;
    dbg_y=y;
    theta += d_theta;

    dbg_dl = left_distance;
    dbg_dr = right_distance;
    dbg_center = distance;
    dbg_theta = theta * 180.0f / PI;

    float inst_linear = d_center / dt;   // cm/s
    float inst_angular = d_theta / dt;   // rad/s

    // --- Moving average filter ---
    ma_linear[ma_idx] = inst_linear;
    ma_angular[ma_idx] = inst_angular;

    ma_idx = (ma_idx + 1) % MA_SIZE;
    if (ma_count < MA_SIZE) ma_count++;

    float sum_linear = 0.0f;
    float sum_angular = 0.0f;
    for (int i = 0; i < ma_count; i++) {
        sum_linear += ma_linear[i];
        sum_angular += ma_angular[i];
    }

    linear_velocity = sum_linear / ma_count;
    angular_velocity = sum_angular / ma_count;

    dbg_linear = inst_linear;
    dbg_angular = inst_angular * 180.0f / PI; // deg/s
}

void Odometry::getSpeed(float &out_linear_velocity, float &out_angular_velocity) const {
    out_linear_velocity = linear_velocity;
    out_angular_velocity = angular_velocity;
}

void Odometry::getPose(float &out_x, float &out_y, float &out_theta, float &out_d_center) const {
    out_x = x;
    out_y = y;
    out_theta = theta;
    out_d_center = distance;
}
