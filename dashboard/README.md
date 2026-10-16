# ZEN-europe dashboard (beta)

A web dashboard to create ZEN-europe datasets: configure model variants with
an explanation for every setting, inspect their sectors, technologies and
carriers, generate and download them, and explore the generated data in
charts and maps.

## Quick start

From the root of the ZEN-europe repository, in the ZEN-europe environment:

```bash
pip install -e ".[dashboard]"

cd dashboard/frontend
npm install          # needs Node.js 20 or newer
npm run build

cd ../backend
python -m zen_dashboard          # http://127.0.0.1:8000
```

For frontend development, run `npm run dev` in `frontend/` in a second
terminal (http://127.0.0.1:5173, with hot reloading).

The dashboard writes only to `workspace/`, which is ignored by git.

The full documentation, with how to use each view, the files and the
structure of the code, is in
[docs/files/user_guide/dashboard.rst](../docs/files/user_guide/dashboard.rst).
