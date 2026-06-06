# Gradient Descent

Gradient descent is the core optimisation algorithm for training neural networks. It minimises a loss function by iteratively moving parameters in the direction of steepest descent.

## The Update Rule
`θ ← θ - η · ∇_θ L(θ)`

where θ are the parameters, η is the learning rate, and ∇_θ L is the gradient of the loss with respect to θ.

## Variants
### Batch Gradient Descent
Computes the gradient over the entire dataset before each update. Slow for large datasets but gives a stable gradient estimate.

### Stochastic Gradient Descent (SGD)
Uses a single randomly chosen example per update. Fast and noisy — the noise can help escape local minima.

### Mini-batch SGD
Computes the gradient on a small random subset (mini-batch) of the data. Balances speed and stability. The de facto standard.

## Learning Rate
Too high: overshoots minima, loss oscillates or diverges. Too low: convergence is extremely slow. Learning rate schedules (warm-up + cosine decay, step decay) and adaptive optimisers (Adam) address this.

## Adam Optimiser
Combines momentum (exponential moving average of gradients) with adaptive learning rates per parameter (exponential moving average of squared gradients). Converges fast and is robust to hyperparameter choice.

## Saddle Points and Local Minima
In high-dimensional loss landscapes, saddle points (gradient is zero but not a minimum) are more common than local minima. SGD noise helps escape saddle points.

## Gradient Clipping
Clips gradients whose norm exceeds a threshold. Prevents exploding gradients, especially in RNNs and deep transformers.
