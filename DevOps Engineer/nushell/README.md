So the `open` command can be piped to interact with the output, for example:

`open ~/.ss/rsa | xclip -sel c`

Since data is outputted into tables, you need to know how to take data from them, for example:

`oc get secret -n openshift-gitops repo-1834075916 -o yaml | from yaml | select data.sshPrivateKey`

If you wanna take the data, you can just

`oc get secret -n openshift-gitops repo-1834075916 -o yaml | from yaml | get data.sshPrivateKey`