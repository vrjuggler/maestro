# Windows Authentication #

This page contains links, ideas, and other information regarding how to authenticate a user through Maestro on Windows. Authentication is necessary for launched applications to be able to access user data.

## Goals ##

  * **{DONE}** Authentication must work using [normal Windows means](http://msdn.microsoft.com/library/default.asp?url=/library/en-us/secauthn/security/authentication_portal.asp) in order for easy deployment and interoperability with existing Windows networks.
  * **{DONE}** Must support domain and non-domain logins
    * Domain querying needs work.
  * **{READY FOR TESTING}** Utilize credentials via SSPI forwarding when possible.
    * Offers a more transparent utilization of the network resources.
    * Avoids requiring the user to re-enter user name and password (which can be considered a security risk).

### Concepts and Terminology ###

Definition of [access token](http://msdn2.microsoft.com/en-gb/library/ms721532.aspx): "An access token contains the security information for a logon session. The system creates an access token when a user logs on, and every process executed on behalf of the user has a copy of the token. The token identifies the user, the user's groups, and the user's privileges. The system uses the token to control access to securable objects and to control the ability of the user to perform various system-related operations on the local computer. There are two kinds of access token, [primary](http://msdn2.microsoft.com/en-gb/library/ms721603.aspx) and [impersonation](http://msdn2.microsoft.com/en-gb/library/ms721588.aspx)."

Delegation of credentials is crucial for credentials forwarding to work. Consider the case of three machines: the cluster master, a cluster slave, and a file server. The user starts the Maestro GUI on the cluster master which forwards the local credentials to the cluster slave(s). In order for the cluster slave to be able to access the user's files, the credentials must be forwarded yet again. In SSPI parlance, this is known as delegation. For better or for worse, only Kerberos allows delegation. **NTLM does not support delegation** because the user's password is never transmitted across the network. As such, the slave node cannot generate the one-way hash needed for the slave node to forward the forwarded credentials.

### Issues and Unknowns ###

  * Should custom authentication be allowed, or can functions such as `LogonUser()` get by without needing to know about [LSA](http://msdn.microsoft.com/library/en-us/secauthn/security/lsa_authentication.asp) and such?

## Resources ##

### Access Tokens and Delegation ###

  * Windows Server TechCenter article: [How Acess Tokens Work](http://technet2.microsoft.com/WindowsServer/en/library/d06a5070-2a7b-4e75-b7e9-ebe51f65e34b1033.mspx?mfr=true)
  * Microsoft Knowldege Base article: [How To Use Delegation in Windows 2000 with COM+](http://support.microsoft.com/kb/283201)
    * This explains that Active Directory credential delegation as we need it has to be enabled on a _per-machine_ basis on the _domain controller_. As such, it may not be practical for general usage, though it is not beyond the realm of possibility that a domain administrator could trust cluster nodes for delegation. With Windows Server 2003, delegation for computer accounts can be restricted to specific services, so this could alleviate some worry in the minds of domain administrators. Even so, it represents a security hole where a privilege handling bug in the Maestro service could allow elevated privileges to be granted to the GUI user sitting on the client machine.
  * Relevant sections from _The .NET Developer's Guide to Windows Security_ (available from [Amazon](http://www.amazon.com/exec/obidos/tg/detail/-/0321228359)) free ["book-in-a-wiki" site](http://pluralsight.com/wiki/default.aspx/Keith.GuideBook/HomePage.html):
    * [What is Impersonation](http://pluralsight.com/wiki/default.aspx/Keith.GuideBook/WhatIsImpersonation.html)
      * Do not get hung up on all the references to ASP.NET.
    * [What is Delegation](http://www.pluralsight.com/wiki/default.aspx/Keith.GuideBook/WhatIsDelegation.html)
      * In the first paragraph, this section describes the exact case that we need to handle with the Maestro service.
    * [How to Configure Delegation Via Security Policy](http://pluralsight.com/wiki/default.aspx/Keith.GuideBook/HowToConfigureDelegationViaSecurityPolicy.html)
      * [What is a Service Principal Name (SPN)](http://pluralsight.com/wiki/default.aspx/Keith.GuideBook/WhatIsAServicePrincipalNameSPN.html)
      * [How to Use Service Principal Names](http://pluralsight.com/wiki/default.aspx/Keith.GuideBook/HowToUseServicePrincipalNames.html)
      * [How to Get a Token for a User](http://pluralsight.com/wiki/default.aspx/Keith.GuideBook/HowToGetATokenForAUser.html)
        * Includes a trick/hack to use SSPI to work around needing to be the SYSTEM user to be able to call `LogonUser()`.
  * _MSDN Magazine_ article from April 2003: [Exploring S4U Kerberos Extensions in Windows Server 2003](http://msdn.microsoft.com/msdnmag/issues/03/04/SecurityBriefs/)
    * S4U means Service-for-User.
    * This is related to trusting computer accounts for delegation based on the service name.

### Security Support Provider Interface (SSPI) ###

  * [SSPI functions](http://msdn2.microsoft.com/en-gb/library/aa374731.aspx#sspi_functions) (under [authentication functions](http://msdn2.microsoft.com/en-gb/library/aa374731.aspx))
  * [Detailed explanation of SSPI](http://www.microsoft.com/technet/prodtechnol/windows2000serv/maintain/security/sspi2k.mspx) (for Windows Server 2000)
  * [Accessing remote files after impersonation](http://groups.google.com/group/microsoft.public.dotnet.security/browse_thread/thread/1f3ba2cee63e4106/d963849ab918b76f?lnk=st&q=WNetAddConnection2+sspi+ERROR_ACCESS_DENIED&rnum=2&hl=en#d963849ab918b76f)
  * _MSDN Magazine_ article: ["Credentials and Delegation"](http://msdn.microsoft.com/msdnmag/issues/05/09/SecurityBriefs/)
    * This article includes information stating that only Kerberos supports delegation.
  * _MSDN Magazine_ article: ["Explore the Security Support Provider Interface Using the SSPI Workbench Utility"](http://msdn.microsoft.com/msdnmag/issues/0800/security/)
  * MSDN article: [".NET Remoting Authentication and Authorization Sample - Part I"](http://msdn2.microsoft.com/en-us/library/ms973911.aspx)
    * This article includes an explanation of why delegation does not work with NTLM.
  * [Impersonation through SSPI](http://groups.google.com/group/microsoft.public.dotnet.security/browse_frm/thread/775042f6408f711/39c46fec326808e8?lr=&ie=UTF-8&rnum=1&prev=/groups%3Fhl%3Dde%26lr%3D%26ie%3DUTF-8%26selm%3Dacd4da3b.0409080728.2b1fe8e5%2540posting.google.com#39c46fec326808e8)
  * [Creating interactive processes through SSPI](http://groups.google.com/group/microsoft.public.platformsdk.security/browse_thread/thread/cad5c689ea9852c2/2289b181b496f750?lnk=raot)
  * [Discussion about the lack of the INTERACTIVE token after SSPI authentication](http://www.derkeiler.com/Newsgroups/microsoft.public.platformsdk.security/2005-11/0071.html)
    * The [last message](http://www.derkeiler.com/Newsgroups/microsoft.public.platformsdk.security/2005-11/0179.html) says that `AdjustTokenGroups()` cannot be used to add the INTERACTIVE token but that `AddAccessAllowedAce()` can grant execution rights of some form.
  * [Validating user credentials through SSPI](http://support.microsoft.com/default.aspx?scid=kb;en-us;180548)
    * Key statement: "The end result of using the SSPI services to validate the credentials is a logon that is analogous to calling the `LogonUser` API with the `LOGON32_LOGON_NETWORK` logon type. The biggest downside to this type of logon is that you **cannot access remote network resources after impersonating a network type logon**."
  * [Discussion on impersonation without a password](http://groups.google.com/group/microsoft.public.win32.programmer.kernel/browse_thread/thread/8185ad586d5aad80/30b3f0fbffc81aba?lnk=st&q=AcceptSecurityContext+create+local+logon+sid&rnum=1#30b3f0fbffc81aba)
    * The function `NtCreateToken()` is mentioned a few times, and a reference to a book (_Windows NT/2000 Native API Reference_, available from [Amazon](http://www.amazon.com/Windows-2000-Native-API-Reference/dp/1578701996/sr=1-1/qid=1169155219/ref=pd_bbs_sr_1/103-7503245-6733469?ie=UTF8&s=books)) is given.
  * Addison-Wesley article: ["Kerberizing Applications Using Security Support Provider Interface"](http://www.awprofessional.com/articles/article.asp?p=20989&rl=1)
  * microsoft.public.donet.security thread [How does LogonUser API work to prevent impersonating users?](http://groups.google.com/group/microsoft.public.dotnet.security/msg/34e842fa72470c82?q=%22How+does+LogonUser+API+work%22&fwc=1)

### Generic Security Service API (GSSAPI) ###

  * Specified by [IETF RFC 1508](http://www.ietf.org/rfc/rfc1508.txt?number=1508) and [IETF RFC 1509](http://www.ietf.org/rfc/rfc1508.txt?number=1509)

### Security Identifiers (SIDs) ###

  * [SID data structure](http://msdn.microsoft.com/library/default.asp?url=/library/en-us/secauthz/security/sid.asp)
  * [Creating a security descriptor](http://msdn2.microsoft.com/en-us/library/ms707085.aspx) (not the most useful example)
  * [Getting the logon SID in C++](http://msdn2.microsoft.com/en-gb/library/aa446670.aspx)
  * [Searching for a SID in an access token](http://msdn2.microsoft.com/en-us/library/aa379554.aspx)

### Python ###

#### Impersonation ####

[Documentation of impersonation API](http://aspn.activestate.com/ASPN/docs/ActivePython/2.4/pywin32/Windows_NT_Security_.2d.2d_Impersonation.html)

> This shows how to call `LogonUser()` and `ImpersonateLoggedOnUser()` from Python using the [win32api](http://sourceforge.net/projects/pywin32/) extension modules.

[Recipe for impersonating users on Windows](http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81402)

> This recipe uses the impersonation API and has code showing how to adjust the process' privileges so that it can perform the impersonation. The code is not formatted to be readable, however, so here it is a more familiar form:

```
def AdjustPrivilege(priv, enable = 1):
   # Get the process token.
   print priv

   flags = TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
   #flags= TOKEN_QUERY
   htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

   # Get the ID for the privilege.
   id = win32security.LookupPrivilegeValue(None, priv)

   # Now obtain the privilege for this process.
   # Create a list of the privileges to be added.
   if enable:
      newPrivileges = [(id, SE_PRIVILEGE_ENABLED)]
   else:
      newPrivileges = [(id, 0)]

   # and make the adjustment.
   try:
      win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)
   except:
      fail.append(priv)

   # now set the rights
   AdjustPrivilege(SE_CHANGE_NOTIFY_NAME)
   AdjustPrivilege(SE_TCB_NAME)
   AdjustPrivilege(SE_ASSIGNPRIMARYTOKEN_NAME)
```