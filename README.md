# 🎥 GitHub Workflow Video Downloader

A web-based video downloader that uses GitHub Actions workflows to download videos from YouTube and TikTok. The frontend is hosted on GitHub Pages and triggers workflows using the GitHub API.

## ✨ Features

- Download videos from YouTube and TikTok
- Audio-only extraction (MP3)
- Multiple quality options
- GitHub Actions powered backend
- Clean web interface
- Automatic cleanup of old downloads
- Progress tracking and status updates

## 🚀 Setup Instructions

### 1. Repository Setup

1. **Fork or create this repository**
2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / `(root)`

### 2. GitHub Token Setup

1. **Create a Personal Access Token**:
   - Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
   - Click "Generate new token (classic)"
   - Select scopes:
     - `repo` (Full control of private repositories)
     - `workflow` (Update GitHub Action workflows)
   - Copy the token (you'll need it for the website)

### 3. Repository Structure

Make sure your repository has this structure:

```
your-repo/
├── index.html
├── css/style.css
├── js/app.js
├── .github/workflows/
│   ├── download-youtube.yml
│   ├── download-tiktok.yml
│   └── cleanup.yml
├── scripts/
│   ├── youtube_downloader.py
│   └── tiktok_downloader.py
├── downloads/
│   └── .gitkeep
├── requirements.txt
└── README.md
```

### 4. Using the Downloader

1. **Access your GitHub Pages site**: `https://yourusername.github.io/your-repo-name`
2. **Enter your details**:
   - Video URL (YouTube or TikTok)
   - GitHub Token (the one you created)
   - Repository Owner (your GitHub username)
   - Repository Name (this repository's name)
3. **Choose download type**: Video, Audio, or Best Quality
4. **Click "Start Download"**

### 5. How It Works

1. **Frontend triggers workflow**: Using GitHub API with your token
2. **GitHub Actions runs**: Downloads video using yt-dlp
3. **Files are stored**: In the `downloads/` folder
4. **Automatic cleanup**: Old files removed after 24 hours

## 📁 File Access

Downloaded files will be available at:
- Direct link: `https://yourusername.github.io/your-repo-name/downloads/filename.mp4`
- Repository: Check the `downloads/` folder in your repo

## ⚙️ Workflow Details

### YouTube Workflow (`download-youtube.yml`)
- Triggered by: `download-youtube` event
- Downloads: YouTube videos and playlists
- Formats: MP4, MP3, Best quality

### TikTok Workflow (`download-tiktok.yml`)
- Triggered by: `download-tiktok` event
- Downloads: TikTok videos
- Handles: User-agent and headers for TikTok

### Cleanup Workflow (`cleanup.yml`)
- Runs: Daily at 2 AM UTC
- Removes: Files older than 24 hours
- Keeps: Repository clean and under size limits

## 🔒 Security Notes

- **Never commit your GitHub token** to the repository
- Token is entered on the website and used temporarily
- Workflows run in GitHub's secure environment
- Downloads are temporary (24-hour cleanup)

## 🚨 Important Limitations

1. **GitHub Actions Usage**: Free accounts have monthly limits
2. **Repository Size**: GitHub has repository size limits
3. **Public Repository**: Downloads are publicly accessible
4. **Rate Limits**: GitHub API has rate limiting
5. **Legal Compliance**: Ensure you have rights to download content

## 🛠️ Troubleshooting

### Common Issues:

1. **Workflow not triggering**:
   - Check your GitHub token has correct permissions
   - Verify repository owner/name are correct
   - Ensure workflows are enabled in repository settings

2. **Download fails**:
   - Check the Actions tab for error logs
   - Some videos may be region-restricted
   - Private videos cannot be downloaded

3. **Files not appearing**:
   - Wait a few minutes for processing
   - Check the Actions tab for workflow status
   - Large files may take time to upload

### Debugging:

1. **Check workflow logs**: Go to Actions tab → Select the run
2. **Verify file structure**: Ensure all files are in correct locations
3. **Test with simple video**: Try a short, public YouTube video first

## 📝 Customization

You can modify:
- **Download quality**: Edit the Python scripts
- **File formats**: Update yt-dlp options
- **Cleanup schedule**: Modify `cleanup.yml` cron schedule
- **UI styling**: Edit `css/style.css`

## 🔧 Advanced Configuration

### Custom Output Formats

Edit the Python scripts to change output formats:

```python
# In youtube_downloader.py or tiktok_downloader.py
base_options = {
    'format': 'best[height<=1080]',  # Max 1080p
    'outtmpl': '%(title)s_%(uploader)s.%(ext)s',  # Custom naming
}
```

### Extended Cleanup

Modify cleanup schedule in `.github/workflows/cleanup.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

## 📄 License

This project is for educational purposes. Ensure compliance with:
- Platform Terms of Service (YouTube, TikTok)
- Copyright laws in your jurisdiction
- GitHub's Acceptable Use Policy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Open an issue in this repository

---

**⚠️ Disclaimer**: This tool is for personal use only. Respect copyright laws and platform terms of service. Users are responsible for ensuring legal compliance when downloading content.
