#include "motor_controller.hpp"
#include "pid.hpp"
#include "utils.h"
#include <cmath>

#define PWM_MAX 100
#define CONTROL_DT 0.01f
#define VELOCITY_LIMIT_COEF 0.2f
#define MAX_VELOCITY (124.0f*VELOCITY_LIMIT_COEF)
#define MAX_ACCEL 10.0f
//#define KP_linear_velocity 1.0f
//#define KD_linear_velocity 0.0f
//#define KI_linear_velocity 1.0f
//#define KP_linear_velocity 3.32f
//#define KD_linear_velocity 0.6f
//#define KI_linear_velocity 3.18f
#define KP_pos 4.0f
#define KD_pos 0.0f
#define KI_pos 0.0f
//#define KP_linear_velocity 4.8f
//#define KD_linear_velocity 0.7f
//#define KI_linear_velocity 12.00f
#define KP_linear_velocity 1.8f
#define KD_linear_velocity 0.15f
#define KI_linear_velocity 3.65f
#define Kwup_linear_velocity 1.00f//kammoula anti windup

#define KP_angular_velocity 0.90f
#define KD_angular_velocity 0.13f
#define KI_angular_velocity 2.1f
#define KP_ang 6.0f
#define KD_ang 0.0f
#define KI_ang 2.0f
#define MOTOR_CORR_COEF 0.945f
#define MOTOR_POWERUP_COEF 1.055f
#define ANGULAR_VELOCITY_LIMIT_COEF 0.2f
#define MAX_ANGULAR_VELOCITY (8.10f*ANGULAR_VELOCITY_LIMIT_COEF)
#define MAX_ANGULAR_ACCEL 2.5f
TrapezoidProfile profile(MAX_VELOCITY,MAX_ACCEL , MAX_ACCEL , 2.0f, 0.02f);
TrapezoidProfile profile_angle(MAX_ANGULAR_VELOCITY,MAX_ANGULAR_ACCEL , MAX_ANGULAR_ACCEL , 0.0f, 0.02f);;
MotorController::MotorController(TIM_HandleTypeDef* htim_left_,
                                 uint32_t channel_left_,
                                 GPIO_TypeDef* dir1_left_port_, uint16_t dir1_left_pin_,
                                 GPIO_TypeDef* dir2_left_port_, uint16_t dir2_left_pin_,
                                 TIM_HandleTypeDef* htim_right_,
                                 uint32_t channel_right_,
                                 GPIO_TypeDef* dir1_right_port_, uint16_t dir1_right_pin_,
                                 GPIO_TypeDef* dir2_right_port_, uint16_t dir2_right_pin_,
                                 Odometry* odom_)
    : htim_left(htim_left_), channel_left(channel_left_),
      dir1_left_port(dir1_left_port_), dir1_left_pin(dir1_left_pin_),
      dir2_left_port(dir2_left_port_), dir2_left_pin(dir2_left_pin_),
      htim_right(htim_right_), channel_right(channel_right_),
      dir1_right_port(dir1_right_port_), dir1_right_pin(dir1_right_pin_),
      dir2_right_port(dir2_right_port_), dir2_right_pin(dir2_right_pin_),
      odom(odom_),
	  pid_linear_vel(KP_linear_velocity, KI_linear_velocity, KD_linear_velocity, -MAX_VELOCITY, MAX_VELOCITY),
	  pid_pos(KP_pos,KI_pos,KD_pos, -MAX_VELOCITY, MAX_VELOCITY),
	  pid_angle(KP_ang,KI_ang,KD_ang,-MAX_ANGULAR_VELOCITY,MAX_ANGULAR_VELOCITY),
	  pid_angular_vel(KP_angular_velocity,KI_angular_velocity,KD_angular_velocity,-MAX_ANGULAR_VELOCITY,MAX_ANGULAR_VELOCITY)

{
HAL_TIM_PWM_Start(this->htim_left, this->channel_left);
HAL_TIM_PWM_Start(this->htim_right, this->channel_right);

}
float dbg_left_pwm = 0;
float dbg_right_pwm = 0;

int a, b, c, d;

void MotorController::setSpeed(float right_speed, float left_speed) {
    if (left_speed > 1.0f) left_speed = 1.0f;
    if (left_speed < -1.0f) left_speed = -1.0f;
    if (right_speed > 1.0f) right_speed = 1.0f;
    if (right_speed < -1.0f) right_speed = -1.0f;

    HAL_GPIO_WritePin(this->dir1_left_port, this->dir1_left_pin, left_speed >= 0 ? GPIO_PIN_RESET : GPIO_PIN_SET);
    HAL_GPIO_WritePin(this->dir2_left_port, this->dir2_left_pin, left_speed >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);

    HAL_GPIO_WritePin(this->dir1_right_port, this->dir1_right_pin, right_speed >= 0 ? GPIO_PIN_RESET : GPIO_PIN_SET);
    HAL_GPIO_WritePin(this->dir2_right_port, this->dir2_right_pin, right_speed >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);

    __HAL_TIM_SET_COMPARE(this->htim_left, this->channel_left, fabs(left_speed)*PWM_MAX);
    __HAL_TIM_SET_COMPARE(this->htim_right, this->channel_right, fabs(right_speed)*PWM_MAX);

    HAL_TIM_PWM_Start(this->htim_left, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(this->htim_right, TIM_CHANNEL_1);
}

void MotorController::stop() {
    __HAL_TIM_SET_COMPARE(this->htim_left, this->channel_left, 0);
    __HAL_TIM_SET_COMPARE(this->htim_right, this->channel_right, 0);
}

float dbg_v_command = 0;
float dbg_v_command_lim = 0;
float dbg_final_vel=0;
float dbg_v_lin = 0;
float dbg_v_ang=0;
float dbg_error = 0;
float dbg_cmd=0;
float dbg_cmd_anti_wup=0;//kammoula anti windup
float dbg_target_dist=0;
bool inLoop = 0;

void MotorController::moveDistance(float distance_cm) {
    if (!this->odom) return;

    float x0, y0, theta0, d_center0;
    this->odom->getPose(x0, y0, theta0, d_center0);

    uint32_t last = HAL_GetTick();
    float v_command=0.0f;
    float pos_error=0.0f;
    float v_command_lim=0.0f;
    profile.reset();
    while (true) {
    	inLoop=1;
        HAL_Delay(20);

        uint32_t now = HAL_GetTick();
        float dt = (now - last) / 1000.0f;
        if (dt <= 0) dt = CONTROL_DT;
        last = now;

        this->odom->update(dt);

        float x, y, theta, distance;
        this->odom->getPose(x, y, theta, distance);
        float target_distance = distance_cm + d_center0;
        dbg_target_dist=target_distance;

        pos_error = target_distance - distance;
        dbg_error = pos_error;

        v_command=pid_pos.update_pos(pos_error,dt);
        dbg_v_command = v_command;

        if (fabs(pos_error) <= 0.1f) break;  //!!!! danger

        v_command_lim= profile.update_limiter();
        //v_command_lim= profile.update();

        dbg_v_command_lim=v_command_lim;
        dbg_v_command_lim = v_command_lim;
        if (v_command>v_command_lim) {v_command=v_command_lim;}
         dbg_final_vel=v_command;

        float v_lin, v_ang;
        this->odom->getSpeed(v_lin,v_ang);

        dbg_v_lin = v_lin;

        float cmd  = pid_linear_vel.update_speed(v_command, v_lin, dt)/MAX_VELOCITY;
        //float cmd_anti_wup = pid_linear_vel.anti_windup_pid_corr(v_command_lim, v_lin, dt, Kwup_linear_velocity);//kammoula anti windup
        dbg_cmd=cmd;
        //cmd=cmd_anti_wup;//kammoula anti windup
        //dbg_cmd_anti_wup = cmd_anti_wup;//kammoula anti windup
        if (cmd > 1.0f) cmd = 1.0f;
        if (cmd < -1.0f) cmd = -1.0f;

        if ((pos_error > 0 && cmd >0) || (pos_error < 0 && cmd <0) ) setSpeed(cmd*MOTOR_CORR_COEF, cmd); // elli iemes el line hedhi nkassarlou rasou
        else setSpeed(0, 0);
        //setSpeed(0.2, 0.2);
    }

    stop();
    inLoop = 0;
}


void MotorController::moveAngle(float angle_deg) {
    if (!this->odom) return;

    float x0, y0, theta0, d_center0;
    this->odom->getPose(x0, y0, theta0, d_center0);

    uint32_t last = HAL_GetTick();
    float v_current = 0.0f;
    float v_command = 0.0f;
    float angle_error = 0.0f;
    float v_max = MAX_ANGULAR_VELOCITY;
    float v_command_lim = 0.0f;

    profile_angle.reset();

	inLoop=0;

    while (true) {
    	inLoop=1;
        HAL_Delay(20);

        uint32_t now = HAL_GetTick();
        float dt = (now - last) / 1000.0f;
        if (dt <= 0) dt = CONTROL_DT;
        last = now;

        this->odom->update(dt);

        float x, y, theta, distance;
        this->odom->getPose(x, y, theta, distance);

        // Compute angular error (convert to radians if odom uses radians)
        float target_theta = theta0 + DEG2RAD(angle_deg);
        angle_error = target_theta - theta;

        // Normalize angle error to [-pi, pi]
        while (angle_error > 2*M_PI) angle_error -= 2 * M_PI;
        while (angle_error < -2*M_PI) angle_error += 2 * M_PI;

        dbg_error = RAD2DEG(angle_error);

        // PID position controller (for angle)
        v_command = pid_angle.update_pos(angle_error, dt);
        dbg_v_command = v_command;

        if (fabs(angle_error) <= 0.00175f) break; //!!!! danger (angular stop condition)

        v_command_lim = profile_angle.update_limiter();
        //v_command_lim = profile_angle.update();
        dbg_v_command_lim = v_command_lim;

        if (v_command > v_command_lim) {v_command = v_command_lim;}
        dbg_final_vel = v_command;

        float v_lin, v_ang;
        this->odom->getSpeed(v_lin, v_ang);
        dbg_v_ang = v_ang;  // keep for debug, even though we care about v_ang here

        // PID speed controller for angular velocity
        float cmd = pid_angular_vel.update_speed(v_command, v_ang, dt) / MAX_ANGULAR_VELOCITY;
        //dbg_cmd = cmd;

        if (cmd > 1.0f) cmd = 1.0f;
        if (cmd < -1.0f) cmd = -1.0f;

        // Apply differential speed for rotation
        if ((angle_error > 0 && cmd > 0) || (angle_error < 0 && cmd < 0))
            setSpeed(cmd , -cmd*MOTOR_POWERUP_COEF);
        // elli iemes el line hedhi nkassarlou rasou
        else
            setSpeed(0, 0);
        dbg_cmd = cmd;
        //setSpeed(-1, 1);

    }
    inLoop=0;
    stop();
}
