<!-- sparklaunch:connection:start -->
1. Use the standards-based OAuth connection managed by the current host. Never request or accept credentials, bearer tokens, authorization codes, client secrets, or transport headers.
2. If the required SparkLaunch actions are absent, stop before planning or claiming execution. Explain that SparkLaunch is not loaded in this session and direct the user to install or enable this package using the current host's documented flow, then start a fresh session.
3. If a loaded action returns an OAuth challenge, use the current host's documented connect or reconnect flow and retry only after the host reports success. Never use a pasted token as a fallback.
4. If authorization is expired or revoked, stop before any write, reconnect through the current host, and check the target before retrying an uncertain operation.
<!-- sparklaunch:connection:end -->
