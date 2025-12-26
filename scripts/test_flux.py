import torch
from diffusers import StableDiffusionXLPipeline

print(f"🚀 Loading Stable Diffusion XL on {torch.cuda.get_device_name(0)}...")

# Load SDXL model (no authentication needed, smaller download)
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16"
)
pipe.to("cuda")

print("✅ Model loaded! Generating image...")

# Generate an image
prompt = "A neon-lit cyberpunk street in Tokyo at night, rain-soaked pavement reflecting holographic billboards, detailed digital art, 8k, highly detailed"

image = pipe(
    prompt,
    num_inference_steps=30,
    guidance_scale=7.5,
    height=1024,
    width=1024
).images[0]

# Save the image
image.save("outputs/cyberpunk_tokyo.png")
print("✅ Image saved to outputs/cyberpunk_tokyo.png")

# Check GPU memory usage
print(f"🔥 GPU Memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
print(f"🔥 GPU Memory reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")