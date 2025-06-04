# Red Hat OpenShift Pipelines

## Basic Objects

```
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: hello-task
spec:
  steps:
    - name: echo
      image: alpine
      script: |
        #!/bin/sh
        echo "Hello, Tekton!"
```

Task is a Kubernetes object that basically acts like a template. It does not "run" (i.e, no pod will be created when I create a Task object), but runs can occur by referencing this object, for example:

```
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  name: hello-taskrun
spec:
  taskRef:
    name: hello-task
```

Here is a more complicated Task:

```
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: greet
spec:
  params:
    - name: name
      type: string
  results:
    - name: greeting
      description: The greeting output
  steps:
    - name: greet
      image: alpine
      script: |
        #!/bin/sh
        echo "Hello, $(params.name)!" | tee $(results.greeting.path)
```

And now one with volumes:

```
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: kaniko-build
spec:
  params:
    - name: IMAGE
      type: string
  steps:
    - name: build
      image: gcr.io/kaniko-project/executor:latest
      args:
        - "--dockerfile=Dockerfile"
        - "--destination=$(params.IMAGE)"
        - "--context=dir://workspace/source"
      volumeMounts:
        - name: docker-config
          mountPath: /kaniko/.docker
  workspaces:
    - name: source
  volumes:
    - name: docker-config
      configMap:
        name: docker-config
```

We can combine multiple Tasks into on Pipeline, and run them sequantialy:

```
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: sample-pipeline
spec:
  params:
    - name: repo-url
      type: string
    - name: image-url
      type: string
  workspaces:
    - name: shared-workspace
  tasks:
    - name: fetch-repo
      taskRef:
        name: git-clone
      params:
        - name: url
          value: $(params.repo-url)
      workspaces:
        - name: output
          workspace: shared-workspace

    - name: build-image
      runAfter: [fetch-repo]
      taskRef:
        name: kaniko-build
      params:
        - name: IMAGE
          value: $(params.image-url)
      workspaces:
        - name: source
          workspace: shared-workspace
```

Pipelines are somewhat similar to tasks in that they are not creating anything when they are being created. Pipelines are later referenced by PipelineRuns, which pass them specific execution parameters (like volumes, args, etc)

## Events and Triggers

Here is an example of an EventListener:

```
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github-listener
spec:
  serviceAccountName: pipeline
  triggers:
    - name: github-trigger
      bindings:
        - ref: github-binding
      template:
        ref: build-pipeline-template
      interceptors:
        - ref:
            name: github
          params:
            - name: secretRef
              value:
                secretName: github-secret
                secretKey: secretToken
            - name: eventTypes
              value: ["push"]
```

This basically results in the creation of a Service:

```
apiVersion: v1
kind: Service
metadata:
  name: el-github-listener
spec:
  selector:
    eventlistener: github-listener
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

Now lets understand Triggers:

They are also Kubernetes objects, and normally come in 3:

```
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerBinding
metadata:
  name: github-binding
spec:
  params:
    - name: gitrepositoryurl
      value: $(body.repository.clone_url)
    - name: gitrevision
      value: $(body.head_commit.id)
```

```
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerTemplate
metadata:
  name: pipeline-template
spec:
  params:
  - name: gitrevision
    description: The git revision
    default: main
  - name: gitrepositoryurl
    description: The git repository url
  - name: message
    description: The message to print
    default: This is the default message
  - name: contenttype
    description: The Content-Type of the event
  resourcetemplates:
  - apiVersion: tekton.dev/v1beta1
    kind: PipelineRun
    metadata:
      generateName: simple-pipeline-run-
    spec:
      pipelineRef:
        name: simple-pipeline
      params:
      - name: message
        value: $(tt.params.message)
      - name: contenttype
        value: $(tt.params.contenttype)
      - name: git-revision
        value: $(tt.params.gitrevision)
      - name: git-url
        value: $(tt.params.gitrepositoryurl)
      workspaces:
      - name: git-source
        emptyDir: {}
```

```
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerTemplate
metadata:
  name: build-pipeline-template
spec:
  params:
    - name: gitrepositoryurl
    - name: gitrevision
  resourcetemplates:
    - apiVersion: tekton.dev/v1
      kind: PipelineRun
      metadata:
        generateName: build-run-
      spec:
        pipelineRef:
          name: build-pipeline
        params:
          - name: repo-url
            value: $(params.gitrepositoryurl)
          - name: revision
            value: $(params.gitrevision)
        workspaces:
          - name: shared-workspace
            volumeClaimTemplate:
              metadata:
                name: shared-workspace
              spec:
                accessModes: ["ReadWriteOnce"]
                resources:
                  requests:
                    storage: 1Gi
```

```
apiVersion: triggers.tekton.dev/v1beta1
kind: Trigger
metadata:
  name: my-trigger
spec:
  bindings:
    - ref: github-binding
  template:
    ref: build-template
  interceptors:
    - cel:
        filter: "body.ref == 'refs/heads/main'"
```

Which pairs nicely with an EventListener like this:

```
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github-listener
spec:
  serviceAccountName: pipeline
  triggers:
    - triggerRef: my-trigger
```