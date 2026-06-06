# Backpropagation

Backpropagation (backprop) is the algorithm for computing gradients of the loss with respect to every parameter in a neural network. It applies the chain rule of calculus to propagate error signals backwards from the output layer to the input layer.

## The Chain Rule
If L depends on z, and z depends on W, then:
`∂L/∂W = (∂L/∂z) · (∂z/∂W)`

This factorisation means each layer only needs to know its local gradient and the upstream error signal.

## Forward Pass
Each layer computes its output and caches the intermediate values needed to compute gradients later.

## Backward Pass
Starting at the loss, gradients are propagated backwards through each layer in reverse order. Each layer receives `∂L/∂output`, computes `∂L/∂input` and `∂L/∂weights`, and passes `∂L/∂input` upstream.

## Computational Graphs
Modern frameworks (PyTorch, JAX) record operations into a dynamic computational graph. Calling `.backward()` traverses this graph in reverse and accumulates gradients.

## Vanishing Gradients
In deep networks, repeated multiplication of small gradients (e.g. from sigmoid derivatives) can make gradients exponentially small. Solutions include ReLU activations, batch normalisation, residual connections, and careful weight initialisation.

## Exploding Gradients
Gradients can grow exponentially in networks with large weights or RNNs over long sequences. Gradient clipping is the standard remedy.

## Numerical Gradient Checking
Approximate the gradient using finite differences: `(L(θ + ε) - L(θ - ε)) / (2ε)`. Comparing this to the analytic gradient is a debugging tool for catching backprop bugs.
