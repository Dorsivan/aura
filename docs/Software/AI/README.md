Basic Concepts
Model
An ML model, or a model, is a mathematical function that can recognize patterns in data and use those patterns to produce outputs. Rather than programming the model, you must train it by using learning algorithms and data that describe the problem that you want to solve. There are many families of models, and each one has its own algorithms, advantages, disadvantages, and uses cases. Examples of typical models are regression models, decision trees, and neural networks.

Inference
Inference is the process of executing a model as a software function. The model takes a set of inputs, applies the necessary computations to the data, and produces an output. For example, a model in a house pricing scenario might take inputs, such as the size and the number of rooms, and infer the price of a house.

Training
The act of using the data that describes a certain problem, to teach the model how to solve such a problem. Training a model is a repetitive task that typically passes training data to the model to infer the outputs, and compares such outputs with the expected ones. The training algorithm repeats this process, adjusting the coefficients of the model's internal equations, until the outputs of the model are similar to the outputs in the training data. This process is also commonly called fitting.

After training, you can use the model on cases that the model has never seen before. This ability, called generalization, is a key concept in machine learning, and refers to the capacity of models to adapt to unseen data. For example, assume that you want to build an application that can recognize user emotions based on their facial expressions. To this end, you can train a model by using images of user faces, each one tagged with a certain emotion. After training, you can use the model to infer emotions in users that the model has not seen before.

Note
You can also consider a model as a compact representation of the observations that describe a real-world problem. In this context, training is the process of compressing the knowledge of these observations into a smaller artifact: the model.

Features
The model features are the input values that you pass to the model to produce an output. For example, consider a model that recognizes digits in RGB images of 100x100 pixels. Each pixel contains three color channels, and each image contains 10000 pixels. Therefore, the model uses 30000 features, which you must pass to the model to recognize the digit.

From a software perspective, the features define the parameters that you must pass to the model function. Data scientists typically put most of their effort into engineering and selecting the best features for training. If you train a model with a specific set of features, then you must use the same exact features for inference, when the model is in production.

Target Variable(s)
This is the value, or values, that the model tries to infer. Depending on your problem, the model might produce one or more target variables. These variables can be continuous values or categorical values. In a weather forecasting scenario, for example, the temperature is a continuous value, and a severe weather warning is a categorical value (yellow, amber, or red).

Hyperparameters
Parameters specific to the model that configure the structure and the behavior of the model itself. For example, for a decision tree, the depth of the tree and the number of leaf nodes are hyperparameters. The configuration values of the learning algorithm that trains the model are also considered hyperparameters.

During the training phase, data scientists often run multiple training experiments or rounds, each one with different combinations of hyperparameters and features. Then, they compare the experiment outcomes and select the set of hyperparameters that produce the best results. This technique is called hyperparameter tuning.

Evaluation
After a training round, data scientists evaluate the performance of a model on unseen cases. They evaluate the model by using a specific subset of the data that includes samples that the model has not seen during training. Then, they calculate the deviation between the expected values, which are present in the evaluation data set, and the actual values that the model produces. To calculate the deviation, or the performance, data scientists use metrics such as Root-mean-square error, precision, and recall.