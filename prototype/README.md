# Prototype (optional)

Runs the **rule-based scoring step** only. It reads the admin criteria (`criteria.json`) and the
structured facts the AI extraction step would return (`extracted_sample.json`), then prints
ranked / flagged / ineligible results.

```
python score.py                      # uses the two sample files
python score.py --out result.json    # also writes a full point breakdown
```

Python 3.8+, no packages, no API keys needed. Change a weight in `criteria.json` and run again to
see the ranking update without any AI call.
