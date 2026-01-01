# Quick Start - Updated Frontend

## What's New

The frontend now **automatically reads and processes** your GitLab CI files without requiring manual input!

## How It Works

### Step 1: Open the App
- Open `index.html` in your browser
- You'll see the file upload section

### Step 2: Upload Your File
**Option A - Click to Select**
- Click anywhere on the upload area
- Select your `gitlab-ci.yaml` file from your computer

**Option B - Drag and Drop**
- Drag your `gitlab-ci.yaml` file
- Drop it on the upload area

### Step 3: Automatic Processing ⚡
The app will **automatically**:
1. Read the file content
2. Display the file name
3. Populate the editor
4. Start analysis
5. Show results in real-time

## Visual Feedback

### File Loaded Successfully ✓
```
✓ [filename.yaml]  [Change file]
```
- Shows the file name
- "Change file" button appears
- Success message displayed

### Processing
- Loading spinner shows while analyzing
- Status message updates in real-time

### Results
- Dependency graph appears on the left
- GitHub workflow generated on the right
- Variables, secrets, and metrics displayed below

## Features

### 1. **Automatic File Reading**
- No need to copy-paste YAML content
- File is read directly from your system
- Works with .yaml and .yml files

### 2. **One-Click Analysis**
- Just select the file
- Analysis runs automatically
- No manual button clicks needed

### 3. **Easy File Switching**
- Click "Change file" button
- Select a different gitlab-ci.yaml
- Results update automatically

### 4. **Smart Error Handling**
- Clear error messages if file read fails
- Specific validation feedback
- Helpful hints for fixing issues

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` (Win) | Analyze YAML |
| `Cmd+Enter` (Mac) | Analyze YAML |

## Supported File Types

- ✅ `.gitlab-ci.yaml`
- ✅ `.gitlab-ci.yml`
- ✅ Any `.yaml` or `.yml` file

## Limitations

- Maximum file size: 16MB
- Must be valid YAML format
- Requires modern browser (see browser compatibility)

## Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 60+ | ✅ Fully Supported |
| Firefox | 50+ | ✅ Fully Supported |
| Safari | 10+ | ✅ Fully Supported |
| Edge | 79+ | ✅ Fully Supported |
| Mobile | Latest | ✅ Supported |

## Troubleshooting

### File Not Being Read
- Check file format (.yaml or .yml)
- Check file size (max 16MB)
- Try dragging and dropping instead
- Refresh the page and try again

### Analysis Not Starting
- Ensure YAML content is valid
- Check browser console for errors (F12)
- Wait for any previous analysis to complete
- Check that backend API is running (if applicable)

### "Change file" Button Not Working
- Try clicking directly on the button
- Or select a new file from the upload area
- Refresh page if still not working

## Tips & Tricks

1. **Quick Verification**: After upload, verify the file name is displayed correctly
2. **Large Files**: For files > 5MB, expect a short processing delay
3. **Multiple Files**: Use "Change file" to quickly compare different pipelines
4. **Mobile**: Use your device's file picker to select files
5. **Copy Results**: Use the "Copy" button in the GitHub Workflow panel

## API Integration

### Backend Not Available?
- The app has a **demo mode** when the backend API isn't running
- You'll see a warning message
- Basic analysis still works locally
- Full conversion requires backend at `http://localhost:5000`

### To Enable Full Features
1. Start the backend: `python run.py` (in backend folder)
2. Backend will run on `http://localhost:5000`
3. Frontend auto-detects and uses it
4. Full conversion features now available

## Next Steps

1. Select a `gitlab-ci.yaml` file
2. Watch the analysis happen automatically
3. Review the dependency graph
4. Check the GitHub Actions workflow
5. Copy or download the generated workflow
6. Use the "Change file" button to process other files

---

**Questions?** Check the full [FRONTEND_UPDATES.md](FRONTEND_UPDATES.md) or [FILE_PROCESSING_CHANGES.md](FILE_PROCESSING_CHANGES.md) for detailed technical information.
