# Deployment Checklist & Lessons Learned

## Pre-Deployment Checklist

### Environment Configuration
- [ ] `.env` file configured with all required variables
- [ ] `DATABASE_URL` set for production (PostgreSQL on Railway)
- [ ] `OPENAI_API_KEY` configured
- [ ] SMTP credentials added (optional, for email notifications)

### Dependencies
- [ ] `requirements.txt` up to date (`pip freeze > requirements.txt`)
- [ ] All production dependencies included (uvicorn, gunicorn, psycopg2-binary)
- [ ] No dev-only dependencies in requirements.txt

### Railway-Specific Files
- [ ] `Procfile` exists with correct start command
- [ ] `runtime.txt` specifies Python version (e.g., `python-3.11.0`)
- [ ] PostgreSQL database added to Railway project
- [ ] Environment variables set in Railway dashboard

### Frontend
- [ ] API_BASE_URL updated to production URL
- [ ] No trailing slashes in base URLs (causes double-slash in paths)
- [ ] **Cache-busting version parameters added** to JS/CSS files
  - Example: `<script src="app.js?v=1.0.2"></script>`
  - **Increment version on every change to force browser refresh**

### Code Quality
- [ ] Remove debug `print()` statements from production code
- [ ] Remove `console.log()` debug messages (or use conditional logging)
- [ ] HTML escaping for user-generated content (prevent XSS)
- [ ] Event delegation for dynamically generated content (avoid inline onclick)

## Deployment Process

### 1. Local Testing
```bash
# Test locally first
python main.py
# Visit http://localhost:8001
```

### 2. Commit & Push
```bash
git add .
git commit -m "Descriptive commit message"
git push upstream main  # Railway auto-deploys on push
```

### 3. Post-Deployment Verification
- [ ] Check Railway deployment logs for errors
- [ ] Visit production URL and test functionality
- [ ] **Hard refresh browser (Ctrl+Shift+R)** to clear cache
- [ ] Test CRUD operations (Create, Read, Update, Delete)
- [ ] Check browser console for JavaScript errors
- [ ] Verify API calls are hitting correct endpoints

## Common Issues & Solutions

### Issue: "Error loading reminders" / API connection failed
**Solution:** Check that `API_BASE_URL` in `app.js` matches Railway deployment URL

### Issue: Browser shows old cached JavaScript
**Solution:** 
1. Do hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Ensure cache-busting version parameter is updated in `index.html`
3. Increment version: `app.js?v=1.0.X` → `app.js?v=1.0.Y`

### Issue: "Invalid or unexpected token" JavaScript syntax error
**Causes:**
- Inline onclick handlers with unescaped quotes in user data
- Trailing slashes in URLs causing malformed API paths
- Browser caching old broken JavaScript

**Solutions:**
- Use event delegation with `data-` attributes instead of inline onclick
- Add HTML escaping: `${escapeHtml(userInput)}`
- Clear browser cache with hard refresh

### Issue: SQLite errors on Railway
**Solution:** Railway doesn't include SQLite libraries. Add PostgreSQL database in Railway dashboard.

### Issue: DATABASE_URL not recognized
**Solution:** 
- Railway provides `DATABASE_URL` only after PostgreSQL is added
- Check Railway environment variables
- Convert `postgres://` to `postgresql://` for SQLAlchemy compatibility

### Issue: Module not found errors on Railway
**Solution:** Regenerate requirements.txt with `pip freeze > requirements.txt`

## Cache-Busting Strategy

### Why Cache-Busting Matters
Browsers aggressively cache static files (JS, CSS). Without cache-busting, users may see old broken code even after deployment.

### Implementation
Add version query parameters to static file references:

```html
<!-- index.html -->
<link rel="stylesheet" href="styles.css?v=1.0.2">
<script src="app.js?v=1.0.2"></script>
```

### When to Increment Version
**ALWAYS increment the version number when you change:**
- `app.js` - Any JavaScript functionality changes
- `styles.css` - Any styling changes
- Other static assets that change

### Version Numbering
- Use semantic versioning: `v=MAJOR.MINOR.PATCH`
- Example: `v=1.0.0` → `v=1.0.1` for bug fixes
- Example: `v=1.0.1` → `v=1.1.0` for new features
- Or use timestamps: `v=20251030` for simplicity

## Security Best Practices

### Input Validation
- Escape all user-generated content before displaying
- Use `escapeHtml()` function for text that goes into HTML
- Validate on both frontend and backend

### CORS Configuration
- In production, replace `allow_origins=["*"]` with specific domains
- Example: `allow_origins=["https://yourdomain.com"]`

### Sensitive Data
- Never commit `.env` files to git
- Use Railway environment variables for secrets
- Rotate API keys periodically

## Performance Tips

### Database
- Use connection pooling (already configured in `database.py`)
- Add indexes for frequently queried fields
- Use `pool_pre_ping=True` for connection health checks

### Frontend
- Minimize API calls (already using 30-second auto-refresh)
- Use event delegation to reduce event listeners
- Keep JavaScript bundle size small

### Caching
- Static files served by Railway CDN automatically
- Service worker caches for offline PWA functionality
- Cache-busting prevents stale content

## PWA Deployment Notes

### Required Files
- `manifest.json` - PWA configuration
- `service-worker.js` - Offline functionality
- `offline.html` - Fallback page
- App icons (72px, 96px, 128px, 144px, 152px, 192px, 384px, 512px)

### Testing PWA
1. Deploy to HTTPS (Railway provides this automatically)
2. Visit site on mobile device
3. Check for "Add to Home Screen" prompt
4. Test offline functionality

### Path Configuration
- Serve PWA files under `/ui/` path (matches StaticFiles mount)
- Service worker scope: `https://yourapp.railway.app/ui/`
- All cached paths must include `/ui/` prefix

## Railway-Specific Tips

### Auto-Deploy
- Every `git push` to main branch triggers deployment
- Check "Deployments" tab for build logs
- Typical deploy time: 1-2 minutes

### Environment Variables
Add in Railway dashboard under "Variables":
- `DATABASE_URL` - Automatically set when PostgreSQL added
- `OPENAI_API_KEY` - Copy from OpenAI dashboard
- `SMTP_*` variables - For email notifications (optional)

### Logs
- View real-time logs in Railway dashboard
- Use for debugging deployment issues
- Check for startup errors immediately after deploy

### Free Tier Limits
- 500 hours/month execution time
- Projects sleep after inactivity
- First request after sleep may be slow (cold start)

## Troubleshooting Checklist

When something breaks in production:

1. **Check Railway deployment logs** - Look for Python errors
2. **Check browser console** - Look for JavaScript errors
3. **Check Network tab** - See which API calls are failing
4. **Hard refresh browser** - Clear cached files
5. **Check environment variables** - Verify all secrets are set
6. **Test API directly** - Visit `/docs` endpoint for Swagger UI
7. **Compare with local** - Does it work locally?
8. **Check recent commits** - What changed since last working deploy?

## Quick Reference Commands

```bash
# Local development
python main.py

# Update dependencies
pip freeze > requirements.txt

# Git workflow
git status
git add .
git commit -m "Description"
git push upstream main

# Check for Python syntax errors
python -m py_compile filename.py

# Check for JavaScript syntax errors
node -c static/app.js

# View git diff before commit
git diff
```

## Version History

- **v1.0.2** (2025-10-30) - Added cache-busting, fixed edit button, localStorage persistence
- **v1.0.1** (2025-10-29) - Initial Railway deployment with PostgreSQL
- **v1.0.0** (2025-10-28) - MVP release with all Phase 1 features
