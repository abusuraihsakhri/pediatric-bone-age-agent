# Pediatric Bone Age Agent

A descriptive **bone-age comparison** utility with a browser interface, Python API/CLI, and separate demonstration-only rule engines.

**Clinical scope:** The supported calculation subtracts chronological age (months) from an *independently assessed and manually entered* skeletal age (months). Positive values indicate a greater reported skeletal age; negative values indicate a lower one. It does not interpret radiographs, implement Greulich–Pyle atlas matching or Tanner–Whitehouse scoring, establish clinical reference intervals, diagnose disorders, or predict adult height. The optional method field records the source of the entered estimate; selecting it does not run that method.

## Browser application

Open **web/index.html** in a modern browser, or run a local static server:

~~~bash
python -m http.server 8080 --directory web
~~~

Then visit http://localhost:8080. Enter ages (0–240 months), select the reporting method, calculate the signed difference, and optionally download the result as CSV. The page uses only relative assets and has no backend dependency. GitHub Pages publishing is configured in **.github/workflows/pages.yml**; availability depends on enabling Pages with **GitHub Actions** as the publishing source.

## Python installation and usage

Requires Python 3.9 or later.

~~~bash
python -m pip install -e ".[server]"
pediatric-bone-age-engine compare --chronological-months 120 --bone-months 132 --method Greulich-Pyle
~~~

This outputs JSON containing entered ages, the signed difference in months, direction, assessment method, and an explicit limitation statement. Values must be finite numbers between 0 and 240 months.

To run the FastAPI server:

~~~bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve --host 127.0.0.1 --port 8000
~~~

The descriptive comparison endpoint is **POST /api/bone-age/compare**, accepting **chronological_age_months**, **bone_age_months**, and optional **assessment_method** (Unspecified, Greulich-Pyle, Tanner-Whitehouse, or Other). The API also includes older /api/audit, /api/chat, /api/audit/logs, /health, and /metrics endpoints.

For Docker, set AUDIT_SECRET_KEY in your environment and run **docker compose up --build**. The sample Compose configuration publishes only to localhost.

## Legacy modules and limitations

The standalone cli.py audit command, bone_age_sentinel.py, the packaged audit CLI command, and modules in agents/, enrichment.py, and bone_age_sentinel.py contain general-purpose *demonstration* numeric thresholds and status flags. They are retained for backwards compatibility but **are not validated skeletal-age algorithms**. Alerts, severity categories, guideline references in legacy components, mock-LLM output, and nominal or critical labels must not be used for clinical decision-making.

The mock language-model adapter does not invoke an external model or verify clinical findings. The HMAC-SHA256 audit trail operates in memory, needs a user-provided secret, and does not provide durable records or tamper-proof storage.

## Privacy and security

The static browser tool does not upload data, send network requests, use analytics, or retain entered ages beyond the current page session. CSV downloads are generated locally. Do not enter real patient identifiers. The Python server does not implement authentication, role-based access, or regulatory-grade protected health information handling. The heuristic PHI pattern guard does not establish HIPAA compliance. Keep the server private and do not expose it publicly without a separate security review.

Never commit .env or secret keys. See .env.example for the required audit signing key.

## Testing

~~~bash
python -m pip install -e ".[server]" pytest httpx
python -m pytest -q
node --check web/app.js
node --test web/app.test.cjs
~~~

Python regression tests, static JavaScript checks, and package-build checks run in GitHub Actions. Node.js is needed for JavaScript tests, not to run the browser application.

## Technology and license

Python, Pydantic, FastAPI (optional server), standard browser JavaScript/HTML/CSS, and HMAC-SHA256. The browser utility targets browsers supporting ES2015 JavaScript, Blob downloads, and URL.createObjectURL. License: [MIT](LICENSE).
