# Neural Networks

A neural network is a computational graph of connected nodes (neurons) organised in layers. Each layer transforms its input into a higher-level representation.

## Architecture
- **Input layer**: receives raw features.
- **Hidden layers**: apply linear transformations followed by non-linear activation functions.
- **Output layer**: produces the final prediction (e.g. class probabilities via softmax, or a scalar via linear).

## The Neuron
Each neuron computes: `output = activation(W · x + b)` where W is a weight matrix, x is the input vector, b is a bias, and activation is a non-linear function.

## Activation Functions
- **ReLU** (Rectified Linear Unit): `f(x) = max(0, x)`. Cheap, prevents vanishing gradients in deep networks.
- **Sigmoid**: maps to (0,1). Used in binary classification outputs.
- **Tanh**: maps to (-1,1). Zero-centred; often better than sigmoid in hidden layers.
- **GELU**: smoother than ReLU; used in transformers.

## Universal Approximation Theorem
A neural network with at least one hidden layer containing enough neurons can approximate any continuous function to arbitrary precision. This is why deep learning is so expressive.

## Depth vs Width
Deep networks (more layers) learn hierarchical representations. Wide networks (more neurons per layer) have more capacity per layer. In practice, depth tends to be more parameter-efficient than width.

## Batch Normalisation
Normalises each layer's inputs across the batch dimension to have zero mean and unit variance. Stabilises training, allows higher learning rates, and acts as light regularisation.
