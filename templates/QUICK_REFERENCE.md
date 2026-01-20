# 🚀 Project Quick Reference

## 🛠️ Common Commands

| Task | Command | Description |
|------|---------|-------------|
| **Install** | `make install` | Install production dependencies |
| **Dev Setup** | `make dev-install` | Install dev dependencies (pytest, black, etc.) |
| **Run Scraper** | `make run-news` | Run the news aggregator |
| **Test** | `make test` | Run all tests with coverage |
| **Lint** | `make lint` | Check code quality (ruff, mypy) |
| **Format** | `make format` | Auto-format code (black) |
| **Docs** | `make docs-serve` | Preview documentation locally |

## 📂 Key Directories

- `src/common/`: Reusable utilities (browser, logger, config)
- `src/news/`, `src/ecommerce/`: Scraper modules
- `tests/`: Test suite (Unit & Integration)
- `data/`: Scraped output files
- `logs/`: Application logs

## 🧪 Development Workflow

1. **Create Feature Branch**: `git checkout -b feat/my-feature`
2. **Install Dev Deps**: `uv pip sync requirements.txt`
3. **Write Code**: Implement feature in `src/`
4. **Add Tests**: Create tests in `tests/`
5. **Verify**: Run `make test` and `make lint`
6. **Commit**: `git commit -m "feat(module): description"`

## 🔍 Debugging Tips

- **Headless Mode**: Set `HEADLESS=false` in `.env` to see browser
- **Logs**: Check `logs/app.log` for detailed errors
- **Network**: Use `DEBUG=true` to see HTTP requests
