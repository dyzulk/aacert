# Issuing certificates through aaPanel

Once a provider is configured and aacert is enabled:

1. Open **aaPanel Dashboard → Website**.
2. Select **Conf** for the site, then open **SSL**.
3. Choose the **Let's Encrypt** tab. aacert intercepts the aaPanel ACME request
   and routes it to the configured provider.
4. Choose a verification method. DNS verification through a supported DNS
   provider or file verification can be used, depending on the domain.
5. Apply for the certificate and review aaPanel's output for errors.
6. Verify the certificate issuer and coverage after issuance.

The aaPanel UI continues to manage DNS verification and renewals through its
native workflow.

## Restart aaPanel after configuration changes

After switching providers, updating credentials, or enabling/disabling aacert,
restart aaPanel so its background workers reload the current configuration:

```bash
bt restart
```

Depending on the aaPanel version, `bt 1` or `systemctl restart bt` may also be
available.
