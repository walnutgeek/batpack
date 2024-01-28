import cvxpy as cp
import numpy as np
# Generate a random problem
np.random.seed(0)
m, n= 40, 25

A = np.random.rand(m, n)
b = np.random.randn(m)
# Construct a CVXPY problem
x = cp.Variable(n, integer=True)
objective = cp.Minimize(cp.sum_squares(A @ x - b))
prob = cp.Problem(objective)
print("Solving...")
print("Optimal value", prob.solve())

print("Status: ", prob.status)
print("The optimal value is", prob.value)
print("A solution x is")
print(x.value)
