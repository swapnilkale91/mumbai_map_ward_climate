# Machine Learning Basics

Machine learning (ML) is a branch of artificial intelligence that enables systems to learn patterns from data and make decisions with minimal human intervention.

## Supervised Learning
In supervised learning, the model is trained on labelled examples — input-output pairs. The goal is to learn a mapping from inputs to outputs that generalises to unseen data. Common tasks include classification (predicting a discrete label) and regression (predicting a continuous value).

## Unsupervised Learning
Unsupervised learning finds structure in unlabelled data. Clustering groups similar examples together. Dimensionality reduction compresses high-dimensional data into a lower-dimensional representation while retaining structure.

## The Training Loop
1. Forward pass: compute the model's prediction for a batch of inputs.
2. Compute the loss: measure how far the prediction is from the true label.
3. Backward pass: compute gradients of the loss with respect to every parameter.
4. Update: adjust parameters to reduce the loss (see Gradient Descent).

## Generalisation and Overfitting
A model that memorises the training set but fails on new data has overfit. A model that is too simple to capture the true pattern has underfit. The gap between training and validation loss is the primary diagnostic.

## Key Terms
- **Feature**: an input variable used by the model.
- **Label**: the target output.
- **Hyperparameter**: a setting chosen before training (e.g. learning rate, number of layers).
- **Epoch**: one full pass through the training dataset.
