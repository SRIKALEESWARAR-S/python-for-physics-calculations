import torch

# Step 1: Define MSE loss function
def mse_loss(predictions, targets):
    return torch.mean((predictions - targets)**2)

# Step 2: Define targets and predictions
Y_true = torch.tensor([[3.0],[5.0],[7.0],[9.0],[11.0]])
Y_pred = torch.tensor([[2.5],[5.5],[6.0],[9.0],[12.0]])

# Step 3: Compute loss
loss = mse_loss(Y_true,Y_pred)

# Step 4: Print the result
print("MSE Loss:", loss.item())
