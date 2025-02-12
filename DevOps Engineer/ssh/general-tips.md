If you want to connect to a VM using a provided ssh key, you need to:

1. Use `ssh-add` to the fullpath of your key
1. Use `ssh -i <your_key>`

If you want to add your own ssh ket to a vm, you use

`ssh-copy-id -i ~/.ssh/some_public_key.pub user@host`

if you use the default key, you won't need to add `-i` on later logins, but you can use ssh profile to set this to be automatic as well

can't use ssh key for some reason? perhaps the host does not allow it. You can use `ssh -v` for more information.

Cool example of ssh-config:

```
[user@host ~]$ cat ~/.ssh/config
host servera
     HostName                      servera.example.com
     User                          usera
     IdentityFile                  ~/.ssh/id_rsa_servera

host serverb
     HostName                      serverb.example.com
     User                          userb
     IdentityFile                  ~/.ssh/id_rsa_serverb
```

Do you get a host identification error but you are sure everything is ok?

you can use this:

`alias ssh0='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR'`

to ignore that part of ssh