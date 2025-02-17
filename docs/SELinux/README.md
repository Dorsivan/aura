#Troubleshoot SELinux Issues

When applications unexpectedly fail to work due to SELinux access denials, methods and tools are available to resolve these issues. It is helpful to start by understanding some fundamental concepts and behaviors when SELinux is enabled.

SELinux consists of targeted policies that explicitly define allowable actions.

A policy entry defines a labeled process and a labeled resource that interact.

The policy states the process type, and the file or port context, by using labels.

The policy entry defines one process type, one resource label, and the explicit action to allow.

An action can be a system call, a kernel function, or another specific programming routine.

If no entry is created for a specific process-resource-action relationship, then the action is denied.

When an action is denied, the attempt is logged with useful context information.

Red Hat Enterprise Linux provides a stable targeted SELinux policy for almost every service in the distribution. Therefore, it is unusual to have SELinux access problems with common RHEL services when they are configured correctly. SELinux access problems occur when services are implemented incorrectly, or when new applications have incomplete policies. Consider these troubleshooting concepts before making broad SELinux configuration changes.

Most access denials indicate that SELinux is working correctly by blocking improper actions.

Evaluating denied actions requires some familiarity with normal, expected service actions.

The most common SELinux issue is an incorrect context on new, copied, or moved files.

File contexts can be fixed when an existing policy references their location.

Optional Boolean policy features are documented in the _selinux man pages.

Implementing Boolean features generally requires setting additional non-SELinux configuration.

SELinux policies do not replace or circumvent file permissions or access control list restrictions.

When a common application or service fails, and the service is known to have a working SELinux policy, first see the service's _selinux man page to verify the correct context type label. View the affected process and file attributes to verify that the correct labels are set.