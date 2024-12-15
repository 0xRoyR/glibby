# Glibby

Glibby is a Python library designed to automate Azure attack paths. It simplifies and enhances interactions with Azure APIs, making it a powerful tool for developers and security professionals working with Azure environments.

---

## 💡 How Does It Work?

Glibby communicates with the Azure Graph API and Azure Resource Manager (RM) API over HTTPS. It is **not a CLI tool**; instead, it is intended to be imported and used as a Python library within your projects.

The tool draws inspiration from the "BARK" CLI tool by Andy Robbins, offering similar functionality but tailored for Python integration.

---

## 📖 Installation

### Install from PyPI

The easiest way to install Glibby is via PyPI:

```bash
pip install glibby
```

**PyPI URL**: [https://pypi.org/project/glibby/1.0.0/](https://pypi.org/project/glibby/1.0.0/)

---

### Other Installation Methods

#### Install from `.whl` File

If you have downloaded the `.whl` file:

```bash
pip install path/to/glibby-1.0.0-py3-none-any.whl
```

#### Install from Source Code

To install the latest version directly from the source code:

```bash
git clone https://github.com/0xRoyR/glibby.git
cd glibby
pip install .
```

---

## 📖 Usage

While comprehensive documentation is in progress, here’s an overview of the core components:

- **`UserAuthHandler`**:
  - A class for managing authentication for Azure Active Directory (AAD) user accounts.
  - Handles access tokens, refresh tokens, and related operations.

- **`SpnAuthHandler`**:
  - A class for managing authentication for Service Principal Names (SPNs) in AAD.
  - Obtains and refreshes access tokens for SPNs.

- **`GraphOperations`**:
  - A class that interacts with the Azure Graph API.
  - Requires a valid Graph API access token to perform operations like managing users and groups.

- **`RMOperations`**:
  - A class that interacts with the Azure Resource Manager (RM) API.
  - Requires a valid RM API access token to perform operations like managing Azure resources.

---

### 🔧 Example Usage

Here’s a quick example to authenticate to Azure with our user and assign ourselves the "Global Administrator" role

```python
from glibby import UserAuthHandler
from glibby import GraphOperations


def main():
    # Creds
    username = "USERNAME"
    password = "PASSWORD"
    tenant_id = "TENANT_ID"

    # Get Access Token
    weak_user_auth = UserAuthHandler(username=username, password=password)
    access_token = weak_user_auth.get_access_token(tenant_id=tenant_id, resource='graph')
    if not access_token:
        return
    
    # Assign the global administrator role to ourselves (if we have enough permissions to do it)
    graph = GraphOperations(access_token=access_token)
    global_admin = graph.get_role_definition('Global Administrator')
    if not global_admin:
        return
    
    user_id = graph.user.id_from_name(username)['object_id']
    if not user_id:
        return
    
    graph.assign_role_to_object(user_id, global_admin)


if __name__ == '__main__':
    main()
    
```

---

## ⚠️ Notes

- After performing certain operations (e.g., assigning a role to a user or adding a user to a group), include a delay using `time.sleep()` for a few seconds. 
  - **Why?** Azure requires some time to process changes, even if it reports success immediately. Adding a short delay ensures your subsequent operations reflect these updates correctly.

---

## 🙌 Credits

- **[Roy Rahamim](https://twitter.com/0xRoyR)**:
  - Creator and developer of Glibby.
  
- **[Andy Robbins](https://x.com/_wald0)**:
  - Creator of [BARK](https://github.com/BloodHoundAD/BARK), which inspired the development of Glibby.

---

## 🌟 Stay Tuned

Detailed documentation and examples will be released soon! For now, dive in and explore the capabilities of Glibby. Feedback and contributions are always welcome!
