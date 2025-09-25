# docTomd

Utility for converting HTML-based `.doc` exports (such as Confluence exports) into Markdown.

## Usage

```bash
python convert_docs.py [input_path] --output docOut
```

- `input_path` can point to a single `.doc` file or a directory containing multiple `.doc` files. If not provided, `docIn` is used.
- The `--output` (`-o`) option chooses where Markdown files are written (defaults to `docOut`).

The repository includes sample files inside `docIn/`; running the script with no arguments will convert them to Markdown in `docOut/`.
