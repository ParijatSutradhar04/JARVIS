# Alternative Gmail Setup with Service Account (if OAuth continues failing)

## Service Account Setup (Alternative Method)

If you continue getting 403 errors with OAuth, you can use a service account:

### 1. Create Service Account
1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: "jarvis-gmail-service"
4. Click "Create and Continue"
5. Skip role assignment for now
6. Click "Done"

### 2. Create Service Account Key
1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose JSON format
5. Download and save as `service-account.json`

### 3. Enable Domain-Wide Delegation
1. In service account details, check "Enable Google Workspace Domain-wide Delegation"
2. Note the "Unique ID" of the service account

### 4. Authorize in Gmail (Admin Console)
If you have admin access to your domain:
1. Go to Google Admin Console → Security → API Controls
2. Click "Domain-wide Delegation"
3. Add the service account client ID
4. Add scopes: https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.modify

Note: This method is more complex and requires domain admin access or personal Gmail with specific setup.

## Recommended: Fix OAuth First

Try the OAuth fixes above first - they're much simpler and work for personal Gmail accounts.
