# Testing SSH Connectivity (Password and Key Auth)

Basic test to check that you can connect via SSH two different ways: with a password, and with a key.

## 1 - password login
Try to SSH in with the test username and password. If it logs in, run something simple like `echo connected` to make sure we got a real working shell.
If that comes back clean, password auth is good. If it gets rejected, hangs, or times out, that's a fail.

## 2 - key-based login
Same idea, but instead of a password, use the private key to log in as the same user.
Again, once it connects, run that a test command to confirm the session actually works.
If the key gets accepted and the command runs fine, that's a pass.
If the key gets rejected or there's an issue loading it, that's a fail.

### Bonus check for incorrect credentials
Try logging in with a wrong password or key on purpose. The host should reject the connection.

## What "success" looks like
Password works, key works, bad password gets rejected.
All three need to check out for the test to be considered passing.
