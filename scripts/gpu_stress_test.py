import torch
import time

print(f"🚀 GPU Stress Test on {torch.cuda.get_device_name(0)}")
print(f"CUDA Version: {torch.version.cuda}")
print(f"PyTorch Version: {torch.__version__}\n")

# Check initial memory
print(f"Initial GPU Memory: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB\n")

# Create larger tensors on GPU
print("Creating large tensors...")
size = 10240  # Increased from 8192 to 10240 (more compute intensive)

# Generate random matrices
A = torch.randn(size, size, device='cuda', dtype=torch.float32)
B = torch.randn(size, size, device='cuda', dtype=torch.float32)

print(f"Tensor A shape: {A.shape}")
print(f"Tensor B shape: {B.shape}")
print(f"GPU Memory after tensors: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB\n")

# Matrix multiplication benchmark
print("🔥 Running extended matrix multiplication stress test...")
print("This will take ~30 seconds and max out your GPU!")
print("Watch your GPU fans spin up!\n")

num_iterations = 200  # Increased from 50 to 200
start_time = time.time()

for i in range(num_iterations):
    # Matrix multiplication (very GPU intensive)
    C = torch.matmul(A, B)
    
    # Also do element-wise operations to keep GPU hot
    D = C * 2.0 + torch.sin(A)
    
    if (i + 1) % 20 == 0:
        elapsed = time.time() - start_time
        temp_tflops = ((2 * size**3 * (i+1)) / elapsed) / 1e12
        print(f"Iteration {i+1}/{num_iterations} - Elapsed: {elapsed:.2f}s - Current: {temp_tflops:.2f} TFLOPS")

end_time = time.time()
total_time = end_time - start_time

print(f"\n✅ Completed {num_iterations} iterations in {total_time:.2f} seconds")
print(f"Average time per iteration: {total_time/num_iterations:.3f}s")
print(f"Operations per second: {num_iterations/total_time:.2f}")

# FLOPS calculation
flops_per_matmul = 2 * size**3  # Matrix mult is O(n^3)
total_flops = flops_per_matmul * num_iterations
tflops = (total_flops / total_time) / 1e12

print(f"\n🔥 Performance: {tflops:.2f} TFLOPS")
print(f"Peak GPU Memory: {torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB")
print(f"\n💡 Pro tip: Run 'nvidia-smi -l 1' in another window to watch real-time stats!")