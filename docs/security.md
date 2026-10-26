# Security architecture

- Configuration and EAB credentials are stored locally in
  `~/.aacert/config.json`.
- The aaPanel hook runs locally and routes native ACME operations to the
  configured provider.
- Account keys are namespaced by provider so custom CA use does not overwrite
  aaPanel's native Let's Encrypt account key.
- aacert does not send telemetry to third-party servers. ACME requests are sent
  to the configured certificate authority as required to issue and manage
  certificates.

Protect the server account and configuration file with appropriate permissions.
Do not share EAB credentials, private keys, or account tokens.
