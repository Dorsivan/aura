If you have weird errors writing into PVCs in OpenShift, you probably need to update your securityContext:

```
securityContext:
    fsGroups: 1002480000
    seLinuxOptions:
        level: s0:c50,c15
```

What does this mean? Well this is the more complicated part.

Kinda weird that fsGroups requires that, since usually, mounted pvcs are owned by the root group, which our user should belong to (at least, according to the docs)

fsGroups is rather easy to explain, This is a linux user number that OpenShift permits. The question is what numbers are ok. Is any number that is higher than 1000000000 ok? Or does the range matter?

The seLinuxOptions, is the part I really cant explain, however.