# Security and disclosure

Do not post secrets, personal information or security-sensitive details in public issues. Before launch, administrators should enable an appropriate private vulnerability reporting route and document the responsible contact.

If a credential is exposed, revoke it immediately; deleting a file does not erase history. Technical maintainers should restrict workflow permissions, review changes to workflows and keep deployment limited to the main branch. Pull request checks must not use privileged `pull_request_target` execution of contributor code.
