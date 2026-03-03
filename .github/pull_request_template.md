## Summary

> Briefly describe what this PR changes and why.

- 
- 
- 

## How to Run Locally

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python app/api.py
```

Test the endpoint:
```bash
curl http://localhost:5000/items
```

## Test Plan

Describe how you verified the changes work correctly.

- [ ] Ran `pytest` locally — all tests pass
- [ ] Manually tested affected endpoint(s)
- [ ] Tested edge cases (empty list, 404, invalid input)

## Screenshots / Output

> Attach screenshots, curl output, or pytest results if applicable.

```
# paste output here
```

## Checklist

- [ ] Unit tests added / updated
- [ ] Integration tests added / updated
- [ ] Docs / README updated
- [ ] No new warnings or errors in CI
- [ ] Code reviewed by at least one reviewer
