# 🔑 Get HuggingFace Access Token

## Step 1: Create Access Token

1. **Go to**: https://huggingface.co/settings/tokens
2. **Click "New token"**
3. **Configure**:
   - Name: `axiom-ai-space` (or any name)
   - Type: **Write** (needed to push code)
   - Click "Generate token"
4. **Copy the token** (you'll see it only once!)

## Step 2: Use Token to Push

After you have the token, run:

```bash
git push huggingface main
```

When prompted:
- **Username**: Your HuggingFace username (`anudeepp`)
- **Password**: Paste the **access token** (not your password!)

## Alternative: Use Token in URL

You can also embed the token in the URL:

```bash
git remote set-url huggingface https://USERNAME:TOKEN@huggingface.co/spaces/anudeepp/axiom-ai
git push huggingface main
```

Replace:
- `USERNAME` with your HuggingFace username
- `TOKEN` with the access token you created

---

**Quick Link**: https://huggingface.co/settings/tokens

After creating the token, let me know and I'll help you push!

