# 🌐 Spotify Ad Silencer Website

This folder contains the landing page for the Spotify Ad Silencer project.

## 🚀 Deployment

### GitHub Pages (Automated)
The website is automatically deployed to GitHub Pages via GitHub Actions when you:
1. Push changes to the `website/` folder
2. Manually trigger the workflow in Actions tab

**Live URL**: `https://yourusername.github.io/spotify-ad-silencer`

### Setting Up GitHub Pages
1. Go to your repository Settings
2. Navigate to "Pages" in the sidebar
3. Set Source to "GitHub Actions"
4. The workflow in `.github/workflows/deploy-pages.yml` handles the rest

### Local Development
To test the website locally:
```bash
# Simple HTTP server (Python 3)
python -m http.server 8000

# Or use Node.js
npx serve .

# Then visit http://localhost:8000
```

## 📝 Customization

### Update Donation Links
The website includes your PayPal link: https://paypal.me/jacobscode?country.x=SE&locale.x=sv_SE

To update other links:
1. Replace `yourusername` with your GitHub username
2. Add your Bitcoin address if you want crypto donations
3. Update GitHub Sponsors link once approved

### Features
- **Responsive Design**: Works on mobile and desktop
- **Download Links**: Direct links to GitHub releases
- **Donation Integration**: PayPal and GitHub Sponsors
- **Professional Look**: Modern design with Spotify colors

## 🔄 Updates
The website automatically updates when you:
- Create new releases (download links stay current)
- Update donation information
- Modify the website content

Any changes to files in this `website/` folder will trigger a new deployment to GitHub Pages within minutes. 