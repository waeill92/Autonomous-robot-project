# BNO055 STM32 CODE 

## WORK IN PROGRESS

This code is for BNO055 with **STM32F446re**.
We created one to use with STM32 HAL I2C.

It does support FreeRTOS, see `bno055.h`. Uncomment `#define FREERTOS_ENABLED` to enable FreeRTOS.

## Usage

Use CubeMX to init i2c in fast mode.

Copy `bno055.c`, `bno055.h` and `bno055_stm32.h` to your project.

Set BNO055 i2c address in `bno055.h`

```c
#define BNO055_I2C_ADDR    BNO055_I2C_ADDR_LO    // For 0x28
#define BNO055_I2C_ADDR    BNO055_I2C_ADDR_HI    // For 0x29
```

Include `bno055_stm32.h`.
Pass i2c handler to bno055_assignI2C function and set work mode:

```c
bno055_assignI2C(&hi2c1);
bno055_setup();
bno055_setOperationModeNDOF();
```

Then use bno055_getVectorEuler to receive euler angle data:

```c
bno055_vector_t v = bno055_getVectorEuler();
printf("Heading: %.2f Roll: %.2f Pitch: %.2f\r\n", v.x, v.y, v.z);
```

Or use bno055_getVectorLinearAccel to receive Linear Accel data (without Gravity components unlike bno055_getVectorLinearAccel):

```c
bno055_vector_t v = bno055_getVectorLinearAccel();
printf("W: %.2f X: %.2f Y: %.2f Z: %.2f\r\n", v.w, v.x, v.y, v.z);
```

To remap axis, use bno055_setAxisMap in config mode (refer to datasheet page 24):

```c
bno055_axis_map_t axis = {
  .x = BNO055_AXIS_X,
  .x_sign = BNO055_AXIS_SIGN_POSITIVE,
  .y = BNO055_AXIS_Y,
  .y_sign = BNO055_AXIS_SIGN_POSITIVE,
  .z = BNO055_AXIS_Z,
  .z_sign = BNO055_AXIS_SIGN_POSITIVE
};
bno055_setAxisMap(axis);
```
