# Regularisation in Machine Learning

Regularisation techniques reduce overfitting by discouraging the model from fitting noise in the training data.

## L2 Regularisation (Weight Decay)
Adds a penalty proportional to the sum of squared weights to the loss: `L_reg = L + λ Σ wᵢ²`. Encourages small weights. Implemented as `weight_decay` in PyTorch optimisers. Equivalent to a Gaussian prior on weights.

## L1 Regularisation (Lasso)
Penalty proportional to the sum of absolute weights: `L_reg = L + λ Σ |wᵢ|`. Produces sparse weights (many exactly zero). Useful for feature selection.

## Dropout
During training, randomly set a fraction p of neuron activations to zero. Forces the network to learn redundant representations. At inference, activations are scaled by (1-p) (or inverted dropout scales during training). Typical p: 0.1–0.5.

## Early Stopping
Monitor validation loss during training. Stop when validation loss has not improved for N consecutive epochs (patience). Prevents fitting noise that appears late in training.

## Data Augmentation
Artificially expand the training set by applying label-preserving transformations (flips, crops, colour jitter for images; back-translation for text). Effectively increases dataset size at no annotation cost.

## Label Smoothing
Replace hard one-hot targets with soft targets: `y_smooth = (1 - ε) * y_onehot + ε / K`. Prevents overconfident predictions and improves calibration.

## Mixup
Trains on convex combinations of training examples and their labels. `x̃ = λxᵢ + (1-λ)xⱼ`. Promotes linear behaviour between training examples.

## The Bias-Variance Trade-off
High regularisation → high bias (underfitting). Low regularisation → high variance (overfitting). The goal is to find the sweet spot that minimises total generalisation error.
