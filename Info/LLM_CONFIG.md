# LLM Configuration Guide

## Overview

The application uses **`llm_config.json`** to configure LLM API parameters such as model selection, temperature, max tokens, and other API-specific settings.

## Quick Start

### 1. Create Configuration File

```bash
cd life_game
cp llm_config.json.template llm_config.json
```

### 2. Configure Models

The default configuration uses **`gpt-4o-mini`** for cost efficiency:

```json
{
  "openai": {
    "model": "gpt-4o-mini",
    "max_tokens": 150,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "anthropic": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 150,
    "temperature": 0.7,
    "top_p": 1.0
  }
}
```

## Configuration Options

### OpenAI Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `"gpt-4o-mini"` | Model to use (gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-3.5-turbo) |
| `max_tokens` | integer | `150` | Maximum tokens in response |
| `temperature` | float | `0.7` | Randomness (0.0-2.0) |
| `top_p` | float | `1.0` | Nucleus sampling (0.0-1.0) |
| `frequency_penalty` | float | `0.0` | Penalize repeated tokens (-2.0 to 2.0) |
| `presence_penalty` | float | `0.0` | Penalize topics already mentioned (-2.0 to 2.0) |

### Anthropic Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `"claude-3-5-sonnet-20241022"` | Model to use |
| `max_tokens` | integer | `150` | Maximum tokens in response |
| `temperature` | float | `0.7` | Randomness (0.0-1.0) |
| `top_p` | float | `1.0` | Nucleus sampling (0.0-1.0) |

## Model Selection

### OpenAI Models

**Recommended for this app: gpt-4o-mini** (default)

| Model | Cost | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `gpt-4o-mini` | Lowest | Fastest | Good | **Default** - Best value |
| `gpt-4o` | Medium | Fast | Excellent | High quality responses |
| `gpt-4-turbo` | Medium | Medium | Excellent | Complex reasoning |
| `gpt-3.5-turbo` | Very low | Very fast | Decent | Budget option |

**Default**: `gpt-4o-mini` - Excellent quality at low cost

### Anthropic Models

| Model | Cost | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `claude-3-5-sonnet-20241022` | Medium | Fast | Excellent | Default - Balanced |
| `claude-3-5-haiku-20241022` | Low | Very fast | Good | Fast responses |
| `claude-3-opus-20240229` | High | Slower | Best | Maximum quality |

## Configuration Examples

### Cost-Optimized (Default)

```json
{
  "openai": {
    "model": "gpt-4o-mini",
    "max_tokens": 150,
    "temperature": 0.7
  }
}
```

**Cost**: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens

### Quality-Optimized

```json
{
  "openai": {
    "model": "gpt-4o",
    "max_tokens": 200,
    "temperature": 0.8,
    "top_p": 0.95
  }
}
```

### Creative Responses

```json
{
  "openai": {
    "model": "gpt-4o-mini",
    "max_tokens": 200,
    "temperature": 1.0,
    "top_p": 0.9,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.3
  }
}
```

### Concise & Focused

```json
{
  "openai": {
    "model": "gpt-4o-mini",
    "max_tokens": 100,
    "temperature": 0.5,
    "top_p": 0.9,
    "frequency_penalty": 0.2
  }
}
```

### Budget Mode (Anthropic)

```json
{
  "anthropic": {
    "model": "claude-3-5-haiku-20241022",
    "max_tokens": 100,
    "temperature": 0.7
  }
}
```

## Parameter Tuning

### Temperature

Controls randomness in responses:

- **0.0-0.3**: Deterministic, focused
- **0.4-0.7**: Balanced (default: 0.7)
- **0.8-1.0**: Creative, varied
- **1.0-2.0**: Highly random (OpenAI only)

**For this game**: 0.7 works well for conversational NPCs

### Max Tokens

Controls response length:

- **50-100**: Very brief responses
- **100-150**: Short responses (default: 150)
- **150-300**: Medium responses
- **300+**: Long responses

**For this game**: 150 tokens ≈ 2-3 sentences (perfect for NPCs)

### Top P (Nucleus Sampling)

Controls diversity:

- **0.1-0.5**: Conservative, predictable
- **0.6-0.9**: Balanced diversity
- **0.9-1.0**: Maximum diversity (default: 1.0)

### Frequency Penalty (OpenAI)

Reduces repetition:

- **0.0**: No penalty (default)
- **0.5-1.0**: Moderate reduction
- **1.0-2.0**: Strong reduction

### Presence Penalty (OpenAI)

Encourages topic diversity:

- **0.0**: No penalty (default)
- **0.5-1.0**: Moderate diversity
- **1.0-2.0**: Strong diversity

## File Location

The application looks for: `life_game/llm_config.json`

## Fallback Behavior

If `llm_config.json` is missing, defaults are used:
- OpenAI: `gpt-4o-mini`, 150 tokens, temperature 0.7
- Anthropic: `claude-3-5-sonnet-20241022`, 150 tokens, temperature 0.7

## Switching Models

To change the model, edit `llm_config.json`:

```json
{
  "openai": {
    "model": "gpt-4o"  // Changed from gpt-4o-mini
  }
}
```

Restart the application to apply changes.

## Testing Different Configurations

1. Edit `llm_config.json`
2. Restart the application
3. Test chat with NPCs
4. Compare quality/cost
5. Adjust parameters as needed

## Cost Comparison

Based on typical usage (150 tokens per response):

| Model | Cost per 1000 chats | Monthly cost (100 chats/day) |
|-------|---------------------|------------------------------|
| gpt-4o-mini | ~$0.12 | ~$0.36 |
| gpt-3.5-turbo | ~$0.08 | ~$0.24 |
| gpt-4o | ~$1.50 | ~$4.50 |
| gpt-4-turbo | ~$3.00 | ~$9.00 |
| claude-3-5-haiku | ~$0.40 | ~$1.20 |
| claude-3-5-sonnet | ~$1.50 | ~$4.50 |

**Recommended**: `gpt-4o-mini` offers the best value

## Advanced Configuration

### Different Models per NPC Type

Currently not supported, but you can modify `chat_service.py` to use different configurations per NPC.

### Dynamic Parameter Adjustment

The config is loaded once at startup. To change:
1. Edit `llm_config.json`
2. Call `config.reload_secrets()` in Python
3. Or restart the application

## Troubleshooting

### "llm_config.json not found"

**Solution**: Create from template:
```bash
cp llm_config.json.template llm_config.json
```

### "Invalid model name"

**Error**: Model doesn't exist or is deprecated

**Solution**: Check [OpenAI models](https://platform.openai.com/docs/models) or [Anthropic models](https://docs.anthropic.com/claude/docs/models-overview)

### Responses are too long/short

**Solution**: Adjust `max_tokens`:
```json
{
  "openai": {
    "max_tokens": 100  // Shorter responses
  }
}
```

### Responses are too repetitive

**Solution**: Increase `frequency_penalty` (OpenAI):
```json
{
  "openai": {
    "frequency_penalty": 0.5
  }
}
```

### Responses are too random

**Solution**: Decrease `temperature`:
```json
{
  "openai": {
    "temperature": 0.5
  }
}
```

## Best Practices

1. **Start with defaults**: The default config is well-tuned
2. **Test changes**: Try different settings with real NPCs
3. **Monitor costs**: Track API usage in provider dashboard
4. **Balance quality/cost**: gpt-4o-mini is usually sufficient
5. **Adjust gradually**: Change one parameter at a time
6. **Document changes**: Note what works for your use case

## Summary

- ✅ **Default model**: `gpt-4o-mini` (cost-efficient)
- ✅ **Default tokens**: 150 (2-3 sentences)
- ✅ **Default temperature**: 0.7 (balanced)
- ✅ **File location**: `life_game/llm_config.json`
- ✅ **Customizable**: All parameters can be adjusted
- ✅ **Fallback**: Sensible defaults if file missing

For API key configuration, see [CONFIG_FILE_SETUP.md](CONFIG_FILE_SETUP.md)
