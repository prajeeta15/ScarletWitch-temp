import torch

MODEL_PATH = "ai_model/model.pth"


def save_model(model, optimizer):
    """Saves the AI model and optimizer state."""
    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict()
    }, MODEL_PATH)
    print("[✓] Model saved successfully.")


def load_model(model, optimizer):
    """Loads the AI model and optimizer state if available."""
    try:
        checkpoint = torch.load(MODEL_PATH)
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        print("[✓] Model loaded successfully.")
    except FileNotFoundError:
        print("[!] No model found. Starting fresh.")
