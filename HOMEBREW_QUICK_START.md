# 🍺 Homebrew Setup - Quick Reference

## What's Been Done ✅

1. ✅ **Updated GitHub workflow** (`.github/workflows/build-releases.yml`)
   - Added automatic Homebrew formula updates
   - Integrated with existing release process
   - Added Homebrew installation instructions to release notes

2. ✅ **Updated main README** (`README.md`)
   - Added Homebrew as the recommended installation method for macOS
   - Clear installation instructions for users

3. ✅ **Created setup documentation** (`HOMEBREW_SETUP.md`)
   - Complete step-by-step setup guide
   - Troubleshooting instructions
   - Maintenance guidelines

## What You Need to Do 🚀

### Essential Steps (Required)

1. **Create the Homebrew tap repository:**
   ```bash
   # Create new GitHub repo: homebrew-spotify-ad-silencer
   # Must be public and start with 'homebrew-'
   ```

2. **Set up the tap repository:**
   ```bash
   git clone https://github.com/JacobOmateq/homebrew-spotify-ad-silencer.git
   cd homebrew-spotify-ad-silencer
   mkdir Formula
   # Copy the formula from HOMEBREW_SETUP.md
   git add . && git commit -m "Initial setup" && git push
   ```

3. **Create Personal Access Token:**
   - GitHub Settings → Developer settings → Personal access tokens
   - Name: "Homebrew Tap Updates"
   - Scopes: `repo` + `workflow`
   - Copy the token

4. **Add repository secret:**
   - Your main repo → Settings → Secrets and variables → Actions
   - New secret: `HOMEBREW_TAP_TOKEN`
   - Paste the personal access token

### Test the Setup

1. **Create a test release:**
   ```bash
   git tag v1.0.6
   git push origin v1.0.6
   ```

2. **Monitor GitHub Actions** to ensure everything works

3. **Test Homebrew installation:**
   ```bash
brew tap JacobOmateq/spotify-ad-silencer
   brew install spotify-ad-silencer
   ```

## How It Works 🔧

1. **When you create a new release tag** → GitHub Action triggers
2. **Workflow builds all platforms** → Creates release with artifacts
3. **Homebrew job downloads macOS ZIP** → Calculates SHA256
4. **Updates formula in tap repository** → Commits and pushes changes
5. **Users can install with Homebrew** → Gets latest version automatically

## Benefits for Users 🎯

- **One-command installation:** `brew install spotify-ad-silencer`
- **Automatic updates:** `brew upgrade` keeps it current
- **Proper uninstall:** `brew uninstall spotify-ad-silencer`
- **No Python setup required:** Homebrew handles everything
- **Standard macOS experience:** Follows macOS conventions

## File Structure After Setup

```
Your main repo (spotify-ad-silencer):
├── .github/workflows/build-releases.yml  ← Updated with Homebrew job
├── README.md                             ← Updated with Homebrew instructions
├── HOMEBREW_SETUP.md                     ← Detailed setup guide
└── HOMEBREW_QUICK_START.md               ← This file

Your tap repo (homebrew-spotify-ad-silencer):
├── Formula/
│   └── spotify-ad-silencer.rb           ← Auto-updated formula
└── README.md                             ← Tap documentation
```

## Next Steps After Setup

1. **Update your project documentation** to prominently feature Homebrew
2. **Test the installation** on a fresh macOS system
3. **Monitor for issues** and user feedback
4. **Consider submitting to official Homebrew** if you get popular

## Getting Help

- **Detailed setup:** See `HOMEBREW_SETUP.md`
- **Homebrew docs:** https://docs.brew.sh/Formula-Cookbook
- **GitHub Actions:** https://docs.github.com/actions

---

**Ready to go?** Start with creating the `homebrew-spotify-ad-silencer` repository! 🚀 