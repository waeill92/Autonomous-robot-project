/*
 * utils.cpp
 *
 *  Created on: Oct 2, 2025
 *      Author: kfakh
 */
#include "utils.h"
#include <cmath>

TrapezoidProfile::TrapezoidProfile(float v_max, float a_max, float d_max, float t_cruise, float dt) {
    init(v_max, a_max, d_max, t_cruise, dt);
}
void TrapezoidProfile::reset(){
	this->t = 0.0f;
}

void TrapezoidProfile::init(float v_max, float a_max, float d_max, float t_cruise, float dt) {
    this->v_max = v_max;
    this->a_max = a_max;
    this->d_max = d_max;
    this->t_cruise = t_cruise;
    this->dt = dt;

    this->t_acc = v_max / a_max;
    this->t_dec = v_max / d_max;

    this->t = 0.0f;
    this->finished = false;
}

float TrapezoidProfile::update() {
    if (finished) return 0.0f;

    float v = 0.0f;
    float t_total = t_acc + t_cruise + t_dec;

    if (t < t_acc) {
        // acceleration phase
        v = a_max * t;
    } else if (t < (t_acc + t_cruise)) {
        // cruise phase
        v = v_max;
    } else if (t < t_total) {
        // deceleration phase
        float t_in_dec = t - (t_acc + t_cruise);
        v = v_max - d_max * t_in_dec;
        if (v < 0) v = 0.0f;
    } else {
        // finished
        v = 0.0f;
        finished = true;
    }

    t += dt;
    return v;
}

float dbg_breaking_distance = 0;


float TrapezoidProfile::update_limiter()
{
    if (finished) return 0.0f;

    float v = 0.0f;
    float t_total = t_acc + t_cruise;

    if (t < t_acc) {
        // acceleration phase
        v = a_max * t;
    } else if (t < (t_acc + t_cruise)) {
        // cruise phase
        v = v_max;
    } else {
    	v = v_max;
    }

    t += dt;
    return v;
}


bool TrapezoidProfile::isFinished() const {
    return finished;
}

float TrapezoidProfile::getTime() const {
    return t;
}
