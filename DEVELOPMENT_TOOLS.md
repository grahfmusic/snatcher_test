# Snatchernauts Framework - Development Tools Reference

## Game Launcher Script

### Location
- **Script**: `scripts/run-game.sh`
- **Purpose**: Unified game launcher with debugging and linting capabilities

### Basic Usage

```bash
# Normal game launch
scripts/run-game.sh

# Run with debug output and console
scripts/run-game.sh --debug

# Lint code before running game
scripts/run-game.sh --lint

# Show help and options
scripts/run-game.sh --help
```

### Features

#### 🚀 **Game Launch**
- Automatically detects and uses Ren'Py SDK
- Uses `RENPY_SDK` environment variable (defaults to `~/renpy-8.4.1-sdk`)
- Validates SDK installation before launch
- Clean error messages for common issues

#### 🐛 **Debug Mode**
```bash
scripts/run-game.sh --debug
```
- Launches game with debug console visible
- Shows detailed startup information
- Keeps output streams active for troubleshooting

#### 🔍 **Linting Integration**
```bash
scripts/run-game.sh --lint
```
- Runs code linting before game launch
- Uses dedicated `scripts/lint.sh` if available
- Falls back to Ren'Py's built-in linter
- Prevents launching with code errors

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RENPY_SDK` | `~/renpy-8.4.1-sdk` | Path to Ren'Py SDK installation |

### Custom SDK Path
```bash
# Temporary override
RENPY_SDK=/path/to/custom/sdk scripts/run-game.sh

# Permanent override (add to shell profile)
export RENPY_SDK=/path/to/custom/sdk
scripts/run-game.sh
```

### Error Handling

The script provides clear error messages for:
- **Missing SDK**: When RENPY_SDK directory doesn't exist
- **Invalid SDK**: When renpy.sh is not found or executable
- **Unknown Options**: For invalid command line arguments

### Examples

```bash
# Quick development cycle
scripts/run-game.sh --lint --debug

# Production testing
scripts/run-game.sh

# Custom SDK location
RENPY_SDK=/opt/renpy-8.4.1 scripts/run-game.sh --lint
```

## Related Development Tools

### Linting
- **Direct**: `scripts/run-game.sh --lint`
- **Standalone**: `scripts/lint.sh` (if available)
- **Manual**: `~/renpy-8.4.1-sdk/renpy.sh . lint`

### Debugging
- **In-Game Console**: `~` or `Shift+O` keys
- **Debug Launch**: `scripts/run-game.sh --debug`
- **Shader Debug**: Enable `shader_debug_enabled = True` in shader files

### Project Structure
```
snatchernauts_framework/
├── scripts/
│   ├── run-game.sh          # Main launcher (this script)
│   └── lint.sh              # Dedicated linter (optional)
├── game/                    # Game source files
├── DEVELOPMENT_TOOLS.md     # This documentation
└── SHADER_REFERENCE.md      # Shader development docs
```

## Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `scripts/run-game.sh` | Launch game normally |
| `scripts/run-game.sh --debug` | Launch with debug console |
| `scripts/run-game.sh --lint` | Lint then launch |
| `scripts/run-game.sh --help` | Show all options |

## Integration with Other Systems

### Shader Development
- Use `--debug` mode to see shader console output
- Enable `shader_debug_enabled = True` for detailed shader logs
- Lint catches shader syntax errors before runtime

### Room System
- Debug mode shows room loading and object initialization
- Lint validates room configuration syntax
- Error output helps identify room system issues

### Audio System
- Debug mode shows audio file loading and fade operations
- Lint catches audio configuration errors
- Console output displays audio system status

## Troubleshooting

### Common Issues

**"RENPY_SDK directory not found"**
```bash
# Check your SDK installation
ls ~/renpy-8.4.1-sdk/
# Or set custom path
export RENPY_SDK=/your/actual/path/to/renpy-sdk
```

**"renpy.sh not found or not executable"**
```bash
# Make executable
chmod +x ~/renpy-8.4.1-sdk/renpy.sh
# Or check SDK integrity
```

**Lint failures**
```bash
# Run lint separately to see detailed errors
scripts/run-game.sh --lint
# Fix reported issues in game/ directory
```

### Performance Tips
- Use `--debug` mode only during development
- Regular linting prevents runtime errors
- SDK path should be on fast storage (SSD preferred)

## Best Practices

1. **Always lint before committing code**
   ```bash
   scripts/run-game.sh --lint
   ```

2. **Use debug mode for troubleshooting**
   ```bash
   scripts/run-game.sh --debug
   ```

3. **Set RENPY_SDK in shell profile for convenience**
   ```bash
   echo 'export RENPY_SDK=~/renpy-8.4.1-sdk' >> ~/.zshrc
   ```

4. **Check script help when in doubt**
   ```bash
   scripts/run-game.sh --help
   ```

This script streamlines the development workflow by combining game launching, debugging, and quality assurance in a single, reliable tool.
