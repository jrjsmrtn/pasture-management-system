<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Recording BDD Test Videos with Playwright

This guide shows how to record videos of your BDD tests using Playwright's built-in video recording feature.

## Quick Start

### Option 1: Enable Video for All Tests

```bash
# Set environment variable
export PLAYWRIGHT_VIDEO=on

# Run your tests
behave features/cmdb/create_ci.feature

# Videos saved to: videos/
```

### Option 2: Enable Video for Failed Tests Only

```bash
# Set to record only failures
export PLAYWRIGHT_VIDEO=retain-on-failure

# Run tests
behave features/cmdb/

# Only failed scenarios will have videos
```

## Configuration

### Enable Video Recording in Playwright Config

Edit `tests/config/playwright_config.py`:

```python
# Context configuration
CONTEXT_CONFIG: dict[str, Any] = {
    "viewport": VIEWPORT,
    "locale": "en-US",
    "timezone_id": "America/New_York",
    "ignore_https_errors": True,
    # Enable video recording
    "record_video_dir": "videos/",  # Directory for video files
    "record_video_size": {"width": 1024, "height": 768},  # Match viewport
}
```

### Update Environment.py

Edit `features/environment.py` to enable video based on environment variable:

```python
import os

def before_scenario(context, scenario):
    """Run before each scenario."""
    # ... existing code ...

    # Enable video recording if requested
    video_mode = os.getenv("PLAYWRIGHT_VIDEO", "off")

    if video_mode != "off":
        context_options = get_context_options()
        context_options["record_video_dir"] = "videos/"
        context_options["record_video_size"] = {"width": 1024, "height": 768}

        if video_mode == "retain-on-failure":
            # Only save videos for failed tests
            context.record_video_mode = "retain-on-failure"

        context.context = context.browser.new_context(**context_options)
    else:
        context.context = context.browser.new_context(**get_context_options())

    # ... rest of existing code ...

def after_scenario(context, scenario):
    """Run after each scenario."""
    # Save video if test failed or if recording all
    video_mode = os.getenv("PLAYWRIGHT_VIDEO", "off")

    if video_mode != "off" and hasattr(context, 'page'):
        video_path = context.page.video.path()

        if video_mode == "retain-on-failure" and scenario.status == "passed":
            # Delete video for passed test
            context.page.video.delete()
        else:
            # Keep video - it will be saved automatically
            print(f"\nVideo saved: {video_path}")

    # ... existing cleanup code ...
```

## Running Tests with Video

### Record Specific Story

```bash
# Record Story 2 tests
export PLAYWRIGHT_VIDEO=on
export HEADLESS=false  # Show browser during recording
behave --tags=@story-2 --tags=@web-ui

# Videos saved to: videos/story-2_*.webm
```

### Record All CMDB Tests

```bash
# Record all CMDB scenarios
export PLAYWRIGHT_VIDEO=on
behave features/cmdb/

# Check videos
ls -lh videos/
```

### Record with Visible Browser

```bash
# Run with browser visible (not headless)
export PLAYWRIGHT_VIDEO=on
export HEADLESS=false
behave features/cmdb/create_ci.feature

# Watch the browser as tests run and record
```

### Record Only Failures

```bash
# Record only failed tests
export PLAYWRIGHT_VIDEO=retain-on-failure
behave features/

# Only scenarios that fail will have videos
```

## Video Output

### Default Settings

- **Format**: WebM (VP8 codec)
- **Resolution**: 1024x768 (matches viewport)
- **Frame rate**: ~25 fps
- **Location**: `videos/` directory
- **Naming**: Automatically named by Playwright

### Example Output

```
videos/
├── create_server_ci-chromium-2025-11-16T18-30-45.webm
├── create_network_device-chromium-2025-11-16T18-31-12.webm
├── link_vm_to_server-chromium-2025-11-16T18-31-45.webm
└── circular_dependency-chromium-2025-11-16T18-32-20.webm
```

## Converting Videos

### WebM to MP4 (for wider compatibility)

```bash
# Install ffmpeg via MacPorts
sudo port install ffmpeg

# Convert single video
ffmpeg -i videos/create_server_ci.webm -c:v libx264 -crf 23 videos/create_server_ci.mp4

# Convert all videos
for f in videos/*.webm; do
    ffmpeg -i "$f" -c:v libx264 -crf 23 "${f%.webm}.mp4"
done
```

### Concatenate Multiple Videos

```bash
# Create file list
echo "file 'create_server_ci.mp4'" > videos/concat.txt
echo "file 'create_network_device.mp4'" >> videos/concat.txt
echo "file 'link_vm_to_server.mp4'" >> videos/concat.txt

# Concatenate
ffmpeg -f concat -safe 0 -i videos/concat.txt -c copy videos/full_demo.mp4
```

## Video Quality Settings

### High Quality (larger files)

```python
CONTEXT_CONFIG = {
    # ...
    "record_video_size": {"width": 1920, "height": 1080},  # Full HD
}
```

### Smaller Files (lower quality)

```python
CONTEXT_CONFIG = {
    # ...
    "record_video_size": {"width": 800, "height": 600},  # Smaller
}
```

## Best Practices

### For Demonstrations

✅ **Run with visible browser** (`HEADLESS=false`)
✅ **Slow down actions** for clarity:

```python
BROWSER_CONFIG = {
    "slow_mo": 500,  # 500ms delay between actions
}
```

✅ **Record in 1080p** for presentations
✅ **Convert to MP4** for compatibility

### For CI/CD

✅ **Record only failures** (`retain-on-failure`)
✅ **Use default resolution** (1024x768)
✅ **Keep as WebM** (smaller files)
✅ **Archive videos** as CI artifacts

### For Debugging

✅ **Record all tests**
✅ **Run with visible browser**
✅ **Add pauses** in step definitions:

```python
context.page.wait_for_timeout(2000)  # 2 second pause
```

## Comparison: Playwright vs OBS

| Feature          | Playwright Video | OBS Studio        |
| ---------------- | ---------------- | ----------------- |
| **Setup**        | Minimal config   | Complex setup     |
| **Automation**   | Fully automated  | Manual start/stop |
| **Scope**        | Per-test videos  | Full session      |
| **Browser sync** | Perfect sync     | May drift         |
| **Terminal**     | Not captured     | Can capture       |
| **Narration**    | No audio         | Can record audio  |
| **Editing**      | None             | Live switching    |
| **CI/CD**        | ✅ Perfect       | ❌ Not practical  |
| **Demo videos**  | ⚠️ Limited       | ✅ Full control   |

### Recommendation

- **For BDD test videos**: Use **Playwright** (automatic, perfect sync)
- **For presentations/demos**: Use **OBS Studio** (terminal + browser + narration)
- **For debugging**: Use **Playwright** with `HEADLESS=false`
- **For documentation**: Use **both** - Playwright for test videos, OBS for walkthroughs

## Example: Record Complete Sprint 4 Demo

```bash
#!/bin/bash
# Record all Sprint 4 CMDB tests

# Setup
export PLAYWRIGHT_VIDEO=on
export HEADLESS=false
export SLOW_MO=300  # Slow down for visibility

# Create output directory
mkdir -p videos/sprint4

# Record Story 1 (Schema)
behave --tags=@story-1 --tags=@cmdb

# Record Story 2 (Create CIs)
behave --tags=@story-2 --tags=@cmdb

# Record Story 3 (Relationships)
behave --tags=@story-3 --tags=@cmdb

# Convert to MP4
for f in videos/*.webm; do
    ffmpeg -i "$f" -c:v libx264 -crf 23 "${f%.webm}.mp4"
    mv "${f%.webm}.mp4" videos/sprint4/
done

# Create summary
echo "Sprint 4 BDD Test Videos" > videos/sprint4/README.txt
ls -lh videos/sprint4/ >> videos/sprint4/README.txt
```

## iTerm2 Integration

While Playwright records the browser, you can use **iTerm2's built-in screen recording** for the terminal:

```bash
# iTerm2: Shell → Start Recording
# Or use AppleScript:
osascript -e 'tell application "iTerm" to tell current session of current window to start recording'

# Run your behave commands
behave features/cmdb/

# Stop recording
osascript -e 'tell application "iTerm" to tell current session of current window to stop recording'

# Recordings saved to: ~/Desktop/recording-*.mov
```

## Troubleshooting

### Videos not being created

**Check**:

1. `record_video_dir` is set in context options
1. Directory exists and is writable: `mkdir -p videos`
1. Playwright version supports video: `pip show playwright`

### Video playback issues

**Solution**: Convert to MP4

```bash
ffmpeg -i input.webm -c:v libx264 output.mp4
```

### Large file sizes

**Solutions**:

- Lower resolution in `record_video_size`
- Use `retain-on-failure` mode
- Compress with ffmpeg: `-crf 28` (higher = smaller/lower quality)

### Videos missing audio

Playwright videos don't capture audio by default. For audio:

- Use OBS Studio, or
- Add narration in post-production, or
- Use iTerm2 recording with system audio

## See Also

- [Playwright Video Documentation](https://playwright.dev/python/docs/videos)
- [OBS Studio Setup](./record-bdd-demo.md) - For full presentations
- [BDD Demo Script](./bdd-demo-script.md) - What to demonstrate
