# OracleXBT Website

Modern landing page for OracleXBT - AI-Powered Prediction Market Intelligence platform.

## Features

- 🎨 Modern animated gradient background
- 🌈 Rainbow animated logo and accents
- 📱 Fully responsive design
- ⚡ Smooth animations and transitions
- 🔴 Live data indicators
- 🎯 Clean, professional UI

## Structure

- `index.html` - Main landing page
- Sections:
  - Hero with CTA
  - Live statistics
  - Feature showcase
  - Live market data
  - Call-to-action
  - Footer

## How to Use

### Local Development

Simply open `index.html` in your browser:

```bash
open website/index.html
# or
python3 -m http.server 8000 --directory website
# Then visit http://localhost:8000
```

### Deploy

This is a static site and can be deployed to:

- **GitHub Pages**: Push to gh-pages branch
- **Vercel**: Connect repo and deploy
- **Netlify**: Drag and drop the website folder
- **Cloudflare Pages**: Connect and deploy

### GitHub Pages Setup

```bash
# Create gh-pages branch
git checkout --orphan gh-pages
git reset --hard
cp -r website/* .
git add .
git commit -m "Deploy OracleXBT website"
git push origin gh-pages

# Access at: https://yourusername.github.io/oraclexbt/
```

## Customization

### Update Links

Replace placeholder links in `index.html`:
- GitHub repository URL
- Twitter/X handle
- Documentation links

### Update Content

- **Hero section**: Modify the main tagline and description
- **Stats**: Update the statistics cards
- **Features**: Customize feature cards
- **Markets**: Add/remove market cards with real data

### Styling

All styles are in the `<style>` tag in `index.html`. Key variables:

```css
:root {
    --dark-bg: #0a0e27;
    --card-bg: #1a1f3a;
    --text-primary: #ffffff;
    --text-secondary: #a8b2d1;
    --accent: #667eea;
}
```

## Integration with Backend

To connect live data:

1. Create an API endpoint that serves market data
2. Update the JavaScript at the bottom of `index.html`
3. Fetch from your API instead of simulated data

Example:

```javascript
async function fetchLiveData() {
    const response = await fetch('/api/markets');
    const data = await response.json();
    updateMarketCards(data);
}
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## License

Same as OracleXBT project
