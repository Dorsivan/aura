## Component

A component:

- Has typed inputs and outputs

- Runs in its own container

- Can be reused across pipelines

- Is declared using @component decorator or YAML + load_component_from_file

### Types of Components

#### Pythonic

```
from kfp.dsl import component

@component
def add(a: int, b: int) -> int:
    return a + b
```

#### Container Based

```
from kfp.components import create_component_from_func

def preprocess(data_path: str) -> str:
    ...
    
preprocess_op = create_component_from_func(preprocess, base_image="python:3.9")
```

Note you can also use Containerized Python components like so:

```
@dsl.component(base_image='python:3.11',
               target_image='gcr.io/my-project/my-component:v1')
def add(a: int, b: int) -> int:
    from math_utils import add_numbers
    return add_numbers(a, b)
```

This page - https://www.kubeflow.org/docs/components/pipelines/user-guides/components/containerized-python-components/ explains this well.

#### Yaml Based

```
name: preprocess
inputs:
  - name: input_path
outputs:
  - name: output_path
implementation:
  container:
    image: my/preprocessor:latest
    command:
      - python
      - preprocess.py
      - --input_path
      - {inputPath: input_path}
      - --output_path
      - {outputPath: output_path}
```

### How to Re-Use

There are several options:
1. Within the same python script, just share it as a library (you can important a specific function, even)
2. Read it as a yaml file
3. Host it in a git repository

## Pipelines

