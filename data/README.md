# Data Directory

This directory contains test data, sample files, and runtime-generated data for the Multi-Agent AI Tour Guide System.

## 📂 Structure

```
data/
└── sample/          # Sample data files and example outputs
    ├── *.json       # Runtime generated (gitignored)
```

## 📝 Files

### Sample Data (`sample/`)

This directory contains example data files used for testing and development:

- **`response.json`** - Example of complete pipeline response
- **`test_waypoints.json`** - Sample waypoint data for testing
- **`waypoints_for_agents.json`** - Preprocessed waypoints ready for agents
- **`waypoints_to_process.json`** - Raw waypoints before processing
- **`youtube_result.json`** - Example YouTube agent response

**Note**: These files are runtime-generated and gitignored. They are created during testing and development.

## 🔄 Runtime Generated Files

Files in `data/sample/*.json` are automatically generated during:
- Pipeline execution
- Integration tests
- Example script runs
- Development testing

These files are useful for:
- Debugging pipeline stages
- Inspecting agent outputs
- Validating data transformations
- Understanding the data flow

## 🚮 Cleanup

To clean up generated data files:

```bash
# Remove all runtime generated JSON files
rm data/sample/*.json

# Or use git clean (careful - removes all untracked files)
git clean -fd data/
```

## ⚠️ Important Notes

- **Do not commit** runtime generated files to git
- **Do not store** sensitive data (API keys, credentials) in this directory
- **Do store** sanitized sample data for testing
- Files in `sample/` directory are gitignored by default

## 📚 Related Documentation

- Test Suite: [`../tests/README.md`](../tests/README.md)
- Examples: [`../examples/README.md`](../examples/README.md)
- Main Documentation: [`../README.md`](../README.md)
