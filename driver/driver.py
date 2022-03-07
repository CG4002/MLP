import pynq.lib.dma
import numpy as np
from pynq import allocate
from pynq import Overlay
import time

print("Running PYNQ Driver")
test_data = np.loadtxt('./driver_content/test_data.txt')
test_label_one_hot = np.loadtxt('./driver_content/test_label_one_hot.txt')
test_label_one_hot = np.loadtxt('./driver_content/test_label.txt')
print("Test data loaded")

BIT_PATH = "./driver_content/mlp_2/mlp.bit"

def predict_once():
    x = test_data[0]
    print(predictor(x))

def predictor(x):
    x = (x * 1024).astype(np.int32)
    # load overlay
    ol = Overlay(BIT_PATH)
    dma = ol.axi_dma_0
    with allocate(shape=(x.shape), dtype=np.int32) as input_buffer:
        input_buffer[:] = x
        with allocate(shape=(16,), dtype=np.int32) as output_buffer:
            dma.sendchannel.transfer(input_buffer)
            dma.recvchannel.transfer(output_buffer)
            dma.sendchannel.wait()
            dma.recvchannel.wait()
            return np.argmax(output_buffer[0:5], axis=0)

def measure_time(x):
    # quantise input
    x = (x * 255).astype(np.int32)
    # load overlay
    ol = Overlay("./driver_content/design_2.bit")
    dma = ol.axi_dma_0
    with allocate(shape=(x.shape), dtype=np.int32) as input_buffer:
        input_buffer[:] = x
        with allocate(shape=(16,), dtype=np.int32) as output_buffer:
            start = time.time()
            dma.sendchannel.transfer(input_buffer)
            dma.recvchannel.transfer(output_buffer)
            dma.sendchannel.wait()
            dma.recvchannel.wait()
            return time.time() - start

predict_once()
