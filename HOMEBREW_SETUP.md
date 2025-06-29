# 🍺 Homebrew Tap Setup Guide

This guide will help you set up automatic Homebrew deployment for your Spotify Ad Silencer project.

## Prerequisites

- GitHub account
- Existing project with GitHub releases workflow
- macOS build artifacts (ZIP files)

## Step 1: Create a Homebrew Tap Repository

1. **Create a new GitHub repository** named `homebrew-spotify-ad-silencer`
   - Repository name MUST start with `homebrew-` for Homebrew to recognize it as a tap
   - Make it public (required for Homebrew taps)
   - Initialize with a README

2. **Clone the repository locally:**
   ```bash
   git clone https://github.com/JacobOmateq/homebrew-spotify-ad-silencer.git
   cd homebrew-spotify-ad-silencer
   ```

3. **Create the Formula directory:**
   ```bash
   mkdir Formula
   ```

4. **Create the initial formula file:**
   ```bash
   cat > Formula/spotify-ad-silencer.rb << 'EOF'
class SpotifyAdSilencer < Formula
  desc "Cross-platform Spotify ad silencer - completely FREE!"
  homepage "https://github.com/JacobOmateq/spotify-ad-silencer"
  url "https://github.com/JacobOmateq/spotify-ad-silencer/releases/download/v1.0.5/SpotifyAdSilencer-darwin-portable.zip"
  sha256 "PLACEHOLDER_SHA256"  # This will be automatically updated by GitHub Actions
  version "1.0.5"
  license "MIT"

  def install
    # Extract the portable app contents
    prefix.install Dir["*"]
    
    # Create a wrapper script for the executable
    (bin/"spotify-ad-silencer").write <<~EOS
      #!/bin/bash
      cd "#{prefix}" && exec "./SpotifyAdSilencer" "$@"
    EOS
    
    # Make the wrapper executable
    chmod 0755, bin/"spotify-ad-silencer"
  end

  def caveats
    <<~EOS
      🎵 Spotify Ad Silencer has been installed!
      
      To start the application:
        spotify-ad-silencer
        
      Important notes:
      • This tool requires the Spotify desktop application (not web player)
      • You may need to grant accessibility permissions on macOS
      • The app will run in the background and automatically detect ads
      
      For support and updates, visit:
      https://github.com/JacobOmateq/spotify-ad-silencer
      
      If this saves you from annoying ads, consider:
      • Starring the GitHub repository ⭐
      • Supporting the developer (see DONATIONS.txt in #{prefix})
    EOS
  end

  test do
    # Basic test to ensure the executable exists and runs
    assert_predicate bin/"spotify-ad-silencer", :exist?
    assert_predicate bin/"spotify-ad-silencer", :executable?
  end
end
EOF
   ```

5. **Create a README for the tap:**
   ```bash
   cat > README.md << 'EOF'
# Homebrew Spotify Ad Silencer Tap

This is a Homebrew tap for the Spotify Ad Silencer application.

## Installation

```bash
# Add the tap
brew tap JacobOmateq/spotify-ad-silencer

# Install the application
brew install spotify-ad-silencer

# Run the application
spotify-ad-silencer
```

## About

Spotify Ad Silencer is a cross-platform tool that automatically detects and silences Spotify advertisements.

- **Main Repository**: https://github.com/JacobOmateq/spotify-ad-silencer
- **License**: MIT
- **Platforms**: macOS, Windows, Linux

## Updating

The formula is automatically updated when new releases are published to the main repository.

## Support

For issues with the application itself, please visit the [main repository](https://github.com/JacobOmateq/spotify-ad-silencer/issues).

For Homebrew-specific issues, please create an issue in this repository.
EOF
   ```

6. **Commit and push the initial setup:**
   ```bash
   git add .
   git commit -m "Initial Homebrew tap setup"
   git push origin main
   ```

## Step 2: Create a Personal Access Token

1. **Go to GitHub Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**

2. **Click "Generate new token (classic)"**

3. **Configure the token:**
   - **Note**: "Homebrew Tap Updates"
   - **Expiration**: Set to "No expiration" or a long duration
   - **Scopes**: Select:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)

4. **Generate the token and copy it** (you won't see it again!)

## Step 3: Add the Token as a Repository Secret

1. **Go to your main project repository** (`spotify-ad-silencer`)

2. **Navigate to Settings** → **Secrets and variables** → **Actions**

3. **Click "New repository secret"**

4. **Create the secret:**
   - **Name**: `HOMEBREW_TAP_TOKEN`
   - **Secret**: Paste the personal access token you created

5. **Click "Add secret"**

## Step 4: Test the Setup

1. **Create a new tag and release** in your main repository:
   ```bash
   git tag v1.0.6
   git push origin v1.0.6
   ```

2. **Monitor the GitHub Actions** to ensure:
   - The build completes successfully
   - The release is created
   - The Homebrew formula is updated automatically

3. **Test the Homebrew installation:**
   ```bash
   brew tap JacobOmateq/spotify-ad-silencer
   brew install spotify-ad-silencer
   spotify-ad-silencer --help  # or however you want to test it
   ```

## Step 5: Update Your Project Documentation

Add Homebrew installation instructions to your main `README.md`:

```markdown
### Installation

#### macOS (Homebrew) - Recommended
```bash
# Add the tap
brew tap JacobOmateq/spotify-ad-silencer

# Install
brew install spotify-ad-silencer

# Run
spotify-ad-silencer
```

#### Manual Installation (All Platforms)
1. Download the appropriate ZIP file from [Releases](https://github.com/JacobOmateq/spotify-ad-silencer/releases)
2. Extract and run the executable
3. Follow the platform-specific setup guide
```

## Troubleshooting

### Formula Update Failures

If the GitHub Action fails to update the formula:

1. **Check the Action logs** for specific error messages
2. **Verify the personal access token** has the correct permissions
3. **Ensure the tap repository exists** and is accessible
4. **Check that the formula syntax is correct**

### SHA256 Mismatch

If users report SHA256 mismatch errors:

1. **Manually verify the SHA256** of your release artifact
2. **Re-run the GitHub Action** to regenerate the formula
3. **Check that the artifact wasn't corrupted** during upload

### Installation Issues

For user installation issues:

1. **Verify Homebrew is up to date**: `brew update`
2. **Check tap is properly added**: `brew tap`
3. **Try reinstalling**: `brew uninstall spotify-ad-silencer && brew install spotify-ad-silencer`

## Advanced Configuration

### Custom Tap Name

If you want to use a different tap name, update these locations:

1. Repository name (must start with `homebrew-`)
2. Workflow file (`git clone` URL)
3. Documentation and installation instructions

### Formula Customization

You can customize the formula by editing `Formula/spotify-ad-silencer.rb`:

- Add dependencies with `depends_on`
- Modify installation steps in the `install` method
- Add additional tests in the `test` block
- Customize the user message in `caveats`

## Maintenance

The formula will be automatically updated when you create new releases. However, you may need to:

1. **Update the token** when it expires
2. **Fix the formula** if breaking changes occur in your app structure
3. **Respond to Homebrew audit issues** if they arise

## Resources

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Creating Homebrew Taps](https://docs.brew.sh/How-to-Create-and-Maintain-a-tap)
- [GitHub Actions Documentation](https://docs.github.com/actions) 