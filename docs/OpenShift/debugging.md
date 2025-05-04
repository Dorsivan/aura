### PVC

Wanna know what is in a pvc? Lets see:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: backstage
  name: debug-deployment
spec:
  selector:
    matchLabels:
      app: name
  replicas: 1
  template:
    metadata:
      labels:
        app: name
    spec:
      volumes:
      - name: debug-volume
        persistentVolumeClaim:
          claimName: backstage-developer-hub-7f8b4885b7-rs8rb-dynamic-plugins-root
      containers:
        - name: container
          image: praqma/network-multitool:latest
          volumeMounts:
            - mountPath: /mnt/db1
              name: debug-volume
```