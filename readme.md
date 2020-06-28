# Monitor your GoDaddy TLS/SSL Certificates

If your organization uses GoDaddy's services for TLS/SSL certification enrollment, you may need to monitor them to prevent "certificate expiration issues".
You can monitor them directly against your web servers (which is the preferred/right way), but in some cases you may find it easier to to this directly through GoDaddy's site.
So, the GoDaddy guys published an API for those things (WARNING: v1 is totally buggy and you shouldn't rely on its responses) and this script uses this API to get the results and send you a nice report directly to your inbox.

## How to use it?

- First, create a new API Key (for production environment) at this page (after login): https://developer.godaddy.com/keys

- Second, Edit the script and set the relevant values at the settings section:
  - shopperId: is the number you login with (also appears in the account settings page).
  - apiKey: The API key you've got at the first step.
  - apiSecret: The API secret you've got at the first step.
  - ignoreExpired: True of False - If you want the report to ignore expired certificates.
  - ignoreRevoked: True of False - If you want the report to ignore revoked certificates.
  - smtpServer: The hostname or ip address of your smtp server.
  - emailSender: The sender email address of the report email.
  - emailRecipients: Comma-separated email addresses list of the report's recipients.
  
- Third, schedule that script according to your needs.
