# Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu/Debian recommended), Windows 10+, macOS 11+
- **RAM**: Minimum 4GB (8GB+ recommended for heavy browser automation)
- **Storage**: 500MB for dependencies, additional space for session history

## Step-by-Step Installation

### 1. System Dependencies (Linux)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk python3-dev

# For desktop automation and OCR (optional)
sudo apt install scrot xdotool tesseract-ocr

# For audio support (optional)
sudo apt install pulseaudio-utils alsa-utils
```

### 2. Python Environment Setup

```bash
# Clone repository
git clone <your-repo-url>
cd smart_agent_system

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Option 1: Install minimal dependencies (recommended)
pip install -r requirements-minimal.txt

# Option 2: Install full environment (all packages)
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env .env.local  # Keep original as template

# Edit with your API keys
nano .env  # or use your preferred editor
```

Required environment variables:
```bash
# At least one API key is required
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key  
ANTHROPIC_API_KEY=sk-your-claude-key

# Reasoning engine (deepseek is most cost-effective)
REASONING_ENGINE=deepseek
```

### 5. Verify Installation

```bash
# Test core functionality
python test_history_module.py

# Test full integration
python test_integration.py

# If tests pass, run the main system
python main.py
```

## API Key Setup Guide

### DeepSeek (Recommended for cost-effectiveness)
1. Visit [https://platform.deepseek.com](https://platform.deepseek.com)
2. Create account and verify email
3. Navigate to API Keys section
4. Create new API key
5. Add to `.env` as `DEEPSEEK_API_KEY=sk-...`

### OpenAI (Required for Browser Use)
1. Visit [https://platform.openai.com](https://platform.openai.com)
2. Create account and add payment method
3. Navigate to API Keys
4. Create new secret key
5. Add to `.env` as `OPENAI_API_KEY=sk-...`

### Anthropic Claude (Optional)
1. Visit [https://console.anthropic.com](https://console.anthropic.com)
2. Create account and add payment method  
3. Navigate to API Keys
4. Create new key
5. Add to `.env` as `ANTHROPIC_API_KEY=sk-...`

## Troubleshooting

### Common Installation Issues

**Permission Errors (Linux)**
```bash
# Fix pip permissions
pip install --user -r requirements-minimal.txt
```

**PyAutoGUI Display Issues (Linux)**
```bash
export DISPLAY=:0
# Or install virtual display
sudo apt install xvfb
```

**Browser Use Installation Problems**
```bash
# Force reinstall browser-use
pip uninstall browser-use
pip install browser-use==0.7.0
```

**Missing System Libraries**
```bash
# Ubuntu/Debian
sudo apt install build-essential libffi-dev libssl-dev

# CentOS/RHEL  
sudo yum install gcc openssl-devel libffi-devel
```

### Performance Optimization

1. **Use SSD storage** for faster session history access
2. **Configure browser settings** in `.env` for your hardware:
   ```bash
   HEADLESS_BROWSER=true  # For better performance
   BROWSER_TIMEOUT=60000  # Increase for slower connections
   ```
3. **Monitor resource usage** with system tools
4. **Clean old sessions** periodically:
   ```bash
   python -c "from shared.history import cleanup_old_sessions; cleanup_old_sessions(7)"
   ```

## Next Steps

After successful installation:
1. Read the main [README.md](README.md) for usage examples
2. Run `python main.py` to start the system
3. Try example commands to test functionality
4. Check `history_data/` for session storage
5. Monitor logs in `logs/` directory (if enabled)
