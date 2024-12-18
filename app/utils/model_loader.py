import torch
from app.utils.avatar_processing import Generator

def load_pretrained_generator(checkpoint_path, num_points, measurement_dim, device='cuda'):
    model = Generator(num_points, measurement_dim)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.to(device)
    return model

def generate_point_cloud(generator, measurements, device='cuda'):
    generator.eval()
    with torch.no_grad():
        measurements = torch.tensor(measurements, dtype=torch.float32).to(device).unsqueeze(0)
        generated_point_cloud = generator(measurements)
        return generated_point_cloud[0].cpu().numpy() 