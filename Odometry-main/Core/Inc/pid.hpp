#pragma once

class PID {
public:
    PID(float kp, float ki, float kd, float out_min = -1.0f, float out_max = 1.0f);

    float update_speed(float setpoint, float measured, float dt);
    void reset();
    float update_pos(float error, float dt);
    float anti_windup_pid_corr(float setpoint, float measured, float dt, float K_wup);//kammoula anti windup

private:
    float kp, ki, kd;
    float integral;
    float prev_error;
    float out_min, out_max;
};
