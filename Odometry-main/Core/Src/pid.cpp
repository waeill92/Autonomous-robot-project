#include "pid.hpp"

PID::PID(float kp, float ki, float kd, float out_min, float out_max)
    : kp(kp), ki(ki), kd(kd), integral(0), prev_error(0),
      out_min(out_min), out_max(out_max) {}

float PID::update_speed(float setpoint, float measured, float dt) {
    float error = setpoint - measured;
    integral += error * dt;
    float derivative = (error - prev_error) / dt;
    prev_error = error;

    float output = kp * error + ki * integral + kd * derivative;
    if (output > out_max) output = out_max;
    if (output < out_min) output = out_min;
    return output;
}

//kammoula anti windup
float PID::anti_windup_pid_corr(float setpoint, float measured, float dt, float K_wup){
	float error = setpoint - measured;
	 float derivative = (error - prev_error) / dt;
	 float unsat_output = kp * error + ki * integral + kd * derivative;
	 float u = 0.0;
	 if(unsat_output > 1){
		 u = 1;
	 }
	 else if (unsat_output < -1){
		 u = -1;
	 }
	 else{
		 u = unsat_output;
	 }
	 float du = u - unsat_output;
	 integral += (error + du * K_wup) * dt;
	 float output = kp * error + ki * integral + kd * derivative;
	  // --- Anti-windup: only integrate if not saturating in same direction as error ---
//	  if (!((output >= out_max && error > 0) || (output <= out_min && error < 0))) {
//	      integral += error * dt;
//	  }
//	  else {
//	      integral *= 0.95f;  // gradual decay
//	  }


	    // Recalculate output after updating integral

	  prev_error = error;

	  return output;

}

float PID::update_pos(float error , float dt) {
    float derivative = (error - prev_error) / dt;
    float output = kp * error + ki * integral + kd * derivative;
    // --- Anti-windup: only integrate if not saturating in same direction as error ---
    if (!((output >= out_max && error > 0) || (output <= out_min && error < 0))) {
        integral += error * dt;
    }
    else {
        integral *= 0.95f;  // gradual decay
    }


    // Recalculate output after updating integral
    output = kp * error + ki * integral + kd * derivative;

    if (output > out_max) output = out_max;
    if (output < out_min) output = out_min;

    prev_error = error;

    return output;
}


void PID::reset() {
    integral = 0;
    prev_error = 0;
}
