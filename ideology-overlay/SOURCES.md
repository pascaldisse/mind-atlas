# Stage 1 corpus sources

## Scope

60 quotation-length passages/corpus; deterministic themed selection in `scripts/build_corpus.py`. Selection terms provide probe coverage only; this is **not** a representative sample of any movement, religion, or belief community.

| corpus | primary text / archive | status |
|---|---|---|
| `left` | Marx & Engels, *The Communist Manifesto* (1848), Project Gutenberg #61 — <https://www.gutenberg.org/ebooks/61> | public domain |
| `right_trad` | Edmund Burke, *Reflections on the Revolution in France* (1790), in Project Gutenberg #15679 — <https://www.gutenberg.org/ebooks/15679> | public domain |
| `qanon` | jkingsman, JSON-QAnon research archive — <https://github.com/jkingsman/JSON-QAnon>; each row also retains its archived-post URL | research archive; Q claims retained for analysis, not endorsed or treated as facts |
| `ufo` | Charles Fort, *The Book of the Damned* (1919), Project Gutenberg #22472 — <https://www.gutenberg.org/ebooks/22472> | public domain; anomalous-phenomena lore, not evidence of UAP claims |
| `scripture` | King James Bible (1611), Project Gutenberg #10 — <https://www.gutenberg.org/ebooks/10>; Edwin Arnold trans., *The Song Celestial / Bhagavad-Gîtâ* (1885), Project Gutenberg #2388 — <https://www.gutenberg.org/ebooks/2388> | public-domain English translations; 30 passages each |

## Reproduction

```sh
python3 ideology-overlay/scripts/build_corpus.py
```

The builder downloads only missing source copies to `ideology-overlay/.cache/` (ignored by git), then replaces the five JSONL files. Every emitted row has exactly `id`, `text`, and `source`.
