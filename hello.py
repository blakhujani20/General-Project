import numpy as np

# Step activation function
def step_function(x):
    return np.where(x >= 0, 1, 0)

class SimpleMLP:
    def __init__(self, input_layer_size, hidden_layer_size, output_layer_size, lr=0.1, epochs=100):
        self.lr = lr
        self.epochs = epochs

        
        self.W1 = np.random.randn(input_layer_size, hidden_layer_size)
        self.B1 = np.random.randn(hidden_layer_size)
        self.W2 = np.random.randn(hidden_layer_size, output_layer_size)
        self.B2 = np.random.randn(output_layer_size)

    def forward(self, x):
        self.hidden_input = np.dot(x, self.W1) + self.B1
        self.hidden_output = step_function(self.hidden_input)
        self.final_input = np.dot(self.hidden_output, self.W2) + self.B2
        self.final_output = step_function(self.final_input)
        return self.final_output

    def train(self, X, y):
        for epoch in range(self.epochs):
            total_error = 0
            for i in range(len(X)):
                
                x_i = X[i]
                target = y[i]
                output = self.forward(x_i)

                error = target - output
                total_error += abs(error)

                # Update weights if there is an error
                if error != 0:
                    self.W2 += self.lr * error * self.hidden_output.reshape(-1, 1)
                    self.B2 += self.lr * error
                    self.W1 += self.lr * error * np.outer(x_i, self.W2.T)
                    self.B1 += self.lr * error * self.W2.T

            # Stop if the total error is 0
            if total_error == 0:
                break

    def evaluate(self, X, y):
        """Evaluate accuracy"""
        predictions = np.array([self.forward(x) for x in X])
        accuracy = np.mean(predictions == y) * 100
        return accuracy

# XOR dataset
X_XOR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_XOR = np.array([[0], [1], [1], [0]])

# Create and train MLP
mlp = SimpleMLP(input_layer_size=2, hidden_layer_size=4, output_layer_size=1, lr=0.1, epochs=100)
mlp.train(X_XOR, y_XOR)

# Evaluate model
accuracy = mlp.evaluate(X_XOR, y_XOR)
print(f"XOR MLP Accuracy: {accuracy:.2f}%")
