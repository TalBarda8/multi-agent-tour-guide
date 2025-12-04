# Examples and Development Scripts

This directory contains example scripts and development tools for the Multi-Agent AI Tour Guide System.

## 📂 Contents

### Main Examples

- **`main.py`** - Primary example demonstrating complete pipeline execution
  - Shows how to use the tour guide system end-to-end
  - Includes error handling and logging examples
  - Good starting point for new users

- **`orchestrate_with_agents.py`** - Advanced orchestration example
  - Demonstrates parallel agent execution
  - Shows how to customize agent behavior
  - Includes timeout and error handling

### Specialized Examples

- **`spotify_finder.py`** - Spotify API integration example
  - Demonstrates music content discovery
  - Shows how to integrate with Spotify API
  - Includes authentication and search examples

### Testing & Development

- **`test_minimal.py`** - Minimal test script for quick validation
  - Lightweight testing script
  - Useful for debugging and quick checks
  - Does not require full environment setup

- **`test_real_agents.py`** - Real agent integration testing
  - Tests actual API integrations (not mocks)
  - Requires API keys to be configured
  - Use with caution (makes real API calls)

## 🚀 Usage

### Running Main Example

```bash
# Ensure dependencies are installed
pip install -r ../requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit .env with your API keys

# Run the main example
python main.py
```

### Running with Mock Mode

Most examples can run in mock mode (no API keys required):

```bash
# Set MOCK_MODE=true in .env
MOCK_MODE=true python main.py
```

### Running Real Agent Tests

```bash
# Requires valid API keys in .env
python test_real_agents.py
```

## ⚠️ Important Notes

- **API Keys**: Real agent tests require valid API keys (Google Maps, YouTube, Spotify)
- **Costs**: Some examples make real API calls which may incur costs
- **Mock Mode**: Use `MOCK_MODE=true` for development without API calls
- **Logging**: Check `../logs/` directory for execution logs

## 📚 Additional Resources

- Main Documentation: [`../README.md`](../README.md)
- Architecture Guide: [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- Testing Guide: [`../docs/guides/TEST_GUIDE.md`](../docs/guides/TEST_GUIDE.md)
- API Documentation: [`../docs/EXTENSIBILITY.md`](../docs/EXTENSIBILITY.md)

## 🤝 Contributing

When adding new examples:
1. Include clear docstrings and comments
2. Add usage instructions to this README
3. Ensure examples work in both mock and real modes
4. Include error handling and logging
5. Keep examples focused and concise
