#include <I2C_LCD_cfg.hpp>
#include "odometry.hpp"
#include "logic.hpp"
#include "motor_controller.hpp"
#include "main.h"
// External handles from CubeMX
extern TIM_HandleTypeDef htim2;
extern TIM_HandleTypeDef htim5;
extern TIM_HandleTypeDef htim1; // left motor PWM
extern TIM_HandleTypeDef htim3; // right motor PWM
extern UART_HandleTypeDef huart2;
extern I2C_HandleTypeDef hi2c1; // i2c LCD Handler
#define MyI2C_LCD I2C_LCD_1
// Global odometry object
Odometry odom(&htim5, &htim2);

// Global motor controller object
MotorController motors(
	&htim3, TIM_CHANNEL_1, GPIOB, GPIO_PIN_6, GPIOA, GPIO_PIN_7,	// left motor
    &htim1, TIM_CHANNEL_1, GPIOC, GPIO_PIN_7, GPIOA, GPIO_PIN_9,   // right motor
    &odom                                                         // pass odometry pointer
);



// Abstract testMotor function
extern "C" void testMotor(void) {
	//motors.moveDistance(102);
	//motors.moveAngle(180);
	//HAL_Delay(3000);x
	//motors.moveDistance(100);
	//HAL_Delay(3000);
	//motors.moveDistance(100);
	//motors.moveAngle(-90);
	//motors.moveAngle(-90);
//	motors.moveAngle(-90);
//	HAL_Delay(10000);
//	motors.moveAngle(45);
//	HAL_Delay(10000);
//	motors.moveAngle(135);
//	HAL_Delay(10000);

}

// robotLoop can be used for other tasks
extern "C" void robotLoop(void) {
	I2C_LCD_Init(MyI2C_LCD);
	I2C_LCD_SetCursor(MyI2C_LCD, 1 , 0);
	I2C_LCD_WriteString(MyI2C_LCD, "Tres");
    I2C_LCD_SetCursor(MyI2C_LCD, 2, 1);
    I2C_LCD_WriteString(MyI2C_LCD, "Professionel");
	//vision_strategy();
}

 void vision_strategy(void){
	motors.moveDistance(21);
	HAL_Delay(1000);
	motors.moveAngle(90);
	HAL_Delay(1000);
	motors.moveAngle(-45);
	HAL_Delay(1000);
	motors.moveAngle(-140);
	HAL_Delay(1000);
	motors.moveAngle(90);
	HAL_Delay(1000);
	motors.moveDistance(100);
}
