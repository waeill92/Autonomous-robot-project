#ifndef TRAPEZOID_PROFILE_H
#define TRAPEZOID_PROFILE_H

#define DEG2RAD(angle_deg) ((angle_deg) * M_PI / 180.0f)
#define RAD2DEG(angle_rad) ((angle_rad) * 180.0f / M_PI)
#include <stdbool.h>
class TrapezoidProfile {
public:
    TrapezoidProfile(float v_max, float a_max, float d_max, float t_cruise, float dt);

    void init(float v_max, float a_max, float d_max, float t_cruise, float dt);

    float update();          // returns velocity at current step
    float update_limiter();
    void reset();
    bool isFinished() const; // check if profile ended
    float getTime() const;   // get current time
    float trapezoidal_limiter(float vel_cmd, float vel_prev,
                              	  	  	  	  	float vmax, float amax, float dt,
    											float distance_remaining);

private:
    float v_max;    // Cruise velocity
    float a_max;    // Acceleration
    float d_max;    // Deceleration
    float t_acc;    // Computed acceleration time
    float t_dec;    // Computed deceleration time
    float t_cruise; // Cruise time
    float dt;       // Step size

    float t;        // Current time
    bool finished;  // Finished flag
};

#endif // TRAPEZOID_PROFILE_H
