
# Glibby
A tool written in to automate Azure attack paths.

## How it works?
Glibby interacts with the Azure Graph API and the Azure Resource Manager API in HTTPS.
This tool should be used as a python library that you import to your code (and not CLI tool).
Glibby is insipired by the "BARK" CLI tool and is similar to it

## Usage
In-Detail Documentation will be posted soon. For now, here is a basic one:
* ```UserAuthHandler``` --> A class that is used in order to obtain access tokens, refresh tokens, etc for user objects in AAD.
* ```SpnAuthHandler``` --> A class that is used in order to obtain access tokens for SPN objects in AAD.
* ```GraphOperations``` --> A class that gets a Graph API access token as parameter and interacts with the Graph API using the token's identity.
* ```RMOperations``` --> A class that gets a RM API access token as parameter and iteracts with the RM API using the token's identity.
  
## Notes
* After doing operations such as assigning user a role, adding a user to group, etc, you should add a sleep command for a couple of seconds.
This is because Azure can't process such operations so quickly and even if it tells you that the operation succeeded, it needs a couple more second to process the changes.

## Credits
[Roy Rahamim](https://twitter.com/0xRoyR) - Coding the tool.

[Andy Robbins](https://x.com/_wald0) - The creator of [BARK](https://github.com/BloodHoundAD/BARK).
