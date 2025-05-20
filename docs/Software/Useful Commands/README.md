## Kubernetes

`kubectl get pods | grep Error | awk {'print $1'} | xargs oc delete pods`

## Docker

`docker rmi $(docker images -f "dangling=true" -q)`

## Certificates

`open_ssl s_client -connect <your_url>:8082 -showcerts < /dev/null > <your_url>.crt`

