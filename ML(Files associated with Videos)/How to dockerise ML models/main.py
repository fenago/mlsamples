from sklearn.linear_model import LinearRegression
import numpy as np

X = np.array([1,2,3,4,5,6,7]).reshape((-1,1))
y = np.array([12,15,17,20,24,30,35]).reshape((-1,1))

linreg = LinearRegression()

linreg.fit(X,y)

inp = np.array([12,14,15]).reshape((-1,1))

print(linreg.predict(inp))