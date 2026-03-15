from ultralytics import YOLO

# Load your trained .pt model
model = YOLO("best.pt")

# Export to ONNX
model.export(format="openvino", imgsz=640 , dynamic=False)  # dynamic=False is easier for NCNN
# from onnxruntime.quantization import quantize_dynamic, QuantType

# model_fp32 = "best.pt"
# model_int8 = "best_int8.pt"

# quantize_dynamic(
#     model_input=model_fp32,
#     model_output=model_int8,
#     weight_type=QuantType.QInt8,  # or QuantType.QUInt8
# )
# print("Quantized model saved to", model_int8)
# model = YOLO(model_int8)
# model.export(format="onnx", imgsz=640 ,simplify=True, dynamic=False)
