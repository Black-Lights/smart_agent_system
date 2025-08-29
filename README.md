# 🤖 Smart Agent System

A powerful multi-agent desktop automation platform that combines browser-based automation with desktop control, featuring intelligent session history and contextual awareness.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Browser Use](https://img.shields.io/badge/Browser%20Use-0.7.0-green.svg)](https://github.com/browser-use/browser-use)

## 🌟 Features

### Core Capabilities
- **🌐 Browser Automation** - Web research, shopping, form filling using Browser Use
- **💻 Desktop Control** - File management, app control, system settings via PyAutoGUI  
- **🧠 Intelligent Routing** - Automatically selects the best agent for each task
- **📖 Session History** - Remembers context across commands with AI-powered summarization
- **💰 Cost-Optimized** - Uses DeepSeek for cheap history processing, OpenAI for execution
- **🔄 Hybrid Workflows** - Seamlessly combines browser and desktop operations

### Advanced Features
- **Context-Aware Agents** - Agents understand previous actions for better decisions
- **Persistent Memory** - Sessions automatically saved and restored
- **Rich Analytics** - Success tracking, agent usage statistics, performance metrics  
- **Multi-LLM Support** - OpenAI, DeepSeek, and Anthropic Claude integration
- **Cross-Platform** - Linux, Windows, and macOS support

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- API keys for at least one LLM provider (OpenAI, DeepSeek, or Anthropic)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd smart_agent_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the system**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# API Keys (at least one required)
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
OPENAI_API_KEY=sk-your-openai-key-here  
ANTHROPIC_API_KEY=sk-your-claude-key-here

# Reasoning Engine Selection
REASONING_ENGINE=deepseek  # deepseek | openai | claude

# Browser Use Configuration  
BROWSER_LLM_MODEL=gpt-4o-mini
HEADLESS_BROWSER=false
BROWSER_TIMEOUT=30000

# Desktop Agent Settings
OCR_LANGUAGE=eng
UI_DETECTION_MODE=windows
SCREENSHOT_DIR=./screenshots

# History & Monitoring
LOG_LEVEL=INFO
ENABLE_DETAILED_LOGS=true
MONITOR_PORT=5050
```

### Recommended API Key Setup

For **cost-effective** operation:
1. **DeepSeek API** - Primary reasoning and history summarization ($0.10/1M tokens)
2. **OpenAI API** - Browser Use agent execution (as needed)

For **maximum capability**:
1. **OpenAI GPT-4** - Best overall performance
2. **Anthropic Claude** - Advanced reasoning capabilities

## 📖 Usage Examples

### Basic Commands

```bash
🎯 What would you like me to do? (or 'quit'): find the best Samsung earphones
🎯 What would you like me to do? (or 'quit'): open calculator and compute 25*47
🎯 What would you like me to do? (or 'quit'): research Python tutorials and save links to file
🎯 What would you like me to do? (or 'quit'): history
```

### Browser Agent Tasks
- Web research and data extraction
- Online shopping and price comparison  
- Social media automation
- Form filling and submissions
- Content scraping and analysis

### Desktop Agent Tasks  
- File and folder management
- Application launching and control
- System settings configuration
- Mathematical calculations
- Screenshot capture
- Terminal command execution

### Hybrid Workflows
- "Download Python tutorial PDFs and organize them in a new folder"
- "Research laptop prices online and create a comparison spreadsheet"
- "Find the weather forecast and set a desktop reminder"

## 🏗️ Architecture

### Core Components

```
smart_agent_system/
├── main.py                    # System entry point
├── core/                      # Core agent logic
│   ├── master_agent.py       # Central orchestrator
│   ├── task_classifier.py    # Task analysis
│   └── result_synthesizer.py # Result processing
├── browser_agent/            # Browser automation
│   ├── core/browser_agent.py # Browser Use integration
│   └── tools/                # Browser control tools
├── desktop_agent/            # Desktop automation  
│   ├── core/desktop_agent.py # PyAutoGUI integration
│   └── tools/                # Desktop control tools
├── reasoning/                # AI reasoning engines
│   ├── task_reasoning.py     # Task analysis
│   ├── step_reasoning.py     # Step generation
│   └── coordination/         # Agent coordination
├── shared/                   # Shared utilities
│   ├── history/              # Session history management
│   ├── utils/                # Common utilities
│   └── monitoring/           # Performance tracking
└── config/                   # Configuration files
```

### History Management System

The history system provides contextual awareness across sessions:

- **SessionHistoryManager** - Core history tracking and retrieval
- **HistorySummarizer** - AI-powered history summarization using DeepSeek
- **Persistent Storage** - Compressed JSON storage with automatic cleanup
- **Context Generation** - Smart context creation for LLM prompts
- **Analytics** - Success rates, agent usage, performance metrics

## 🔧 Development

### Running Tests

```bash
# Test history module
python test_history_module.py

# Test full integration  
python test_integration.py
```

### Project Structure

The system follows a modular architecture:

- **Agents** - Specialized automation agents (browser, desktop)
- **Reasoning** - AI-powered task analysis and planning
- **History** - Context management and session tracking  
- **Coordination** - Inter-agent communication and workflow management
- **Utilities** - Cross-cutting concerns (OS detection, monitoring, etc.)

### Adding New Agents

1. Create agent class in appropriate directory
2. Implement `execute_task(command, context)` method
3. Register with `MasterAgent` routing logic
4. Add configuration options to `.env`

## 📊 Monitoring & Analytics

### Session Statistics
- Task success/failure rates
- Agent usage distribution
- Execution time metrics
- Error frequency analysis

### History Commands
- `history` - View session statistics and recent actions
- Session data automatically persisted to `history_data/`
- Intelligent summarization for long sessions

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**API Key Issues**  
```bash
# Check .env file has valid keys
cat .env | grep API_KEY
```

**Browser Use Problems**
```bash
# Verify OpenAI API key for Browser Use
echo $OPENAI_API_KEY
```

**Desktop Automation Issues**
```bash  
# Install system dependencies
sudo apt-get install python3-tk python3-dev  # Linux
```

### Backup & Recovery

Original files are automatically backed up to `./backups/` before integration.

To restore:
```bash
cp backups/main.py.backup main.py
cp backups/master_agent.py.backup core/master_agent.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Browser Use** - Excellent browser automation framework
- **OpenAI** - GPT models for intelligent task execution  
- **DeepSeek** - Cost-effective AI reasoning
- **PyAutoGUI** - Desktop automation capabilities
- **Rich** - Beautiful terminal interfaces

## 📞 Support

- 📧 Email: your-email@example.com
- 💬 Discord: your-discord-server
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/smart-agent-system/issues)

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Multi-user session support
- [ ] Plugin system for custom agents
- [ ] Web dashboard for monitoring
- [ ] Voice command integration  
- [ ] Mobile app companion

### Version 1.1 (In Progress)
- [x] Session history and context awareness
- [x] Multi-LLM provider support
- [x] Cost optimization with DeepSeek
- [ ] Enhanced error recovery
- [ ] Performance optimizations

---

**Built with ❤️ for intelligent automation**
