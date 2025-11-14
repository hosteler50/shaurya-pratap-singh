PythonAnywhere Quick Deploy — Hostel Review Website

Overview
- Goal: Make the current Excel-backed Flask app public quickly using PythonAnywhere.
- Two fast methods: (A) Deploy from GitHub (recommended), (B) Upload a ZIP via PythonAnywhere Files UI.

Pre-checks (locally)
1. Ensure `app.py` exposes the Flask app as `app` (i.e. `app = Flask(__name__)`).
2. Make sure `requirements.txt` in the repo is up-to-date.
3. Ensure the following folders/files exist in the project root: `data/` (contains `hostels.xlsx`), `static/`, `templates/`.
4. Commit and push your project to a GitHub repo (recommended) or prepare a ZIP.

Recommended: Deploy from GitHub (fast & repeatable)
1. Create a GitHub repo and push your project there.
   - Example (PowerShell):
     ```powershell
     git init
     git add .
     git commit -m "Initial commit for PythonAnywhere deploy"
     git branch -M main
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
     git push -u origin main
     ```
2. Sign in to PythonAnywhere and go to the "Web" tab.
3. Click "Add a new web app" → choose "Manual configuration" → pick the same Python version you used locally (e.g. 3.10).
4. In the "Source code" section, set the working directory to `/home/YOUR_PYANYWHERE_USERNAME/YOUR_REPO` (the location where you'll clone the repo).
5. Open a Bash console on PythonAnywhere (Consoles → Bash) and run:
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   python3 -m venv venv
   . venv/bin/activate
   pip install -r requirements.txt
   mkdir -p data static/uploads
   ```
   - Ensure `data/hostels.xlsx` exists. If you want to upload an existing `hostels.xlsx`, use the Files tab on PythonAnywhere to upload it into the `data/` directory.
6. Configure the WSGI file (open the file from the Web tab: it will be something like `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`). Replace its content with the WSGI template below (use your actual path and username):
   ```python
   import sys
   import os
   # adjust this to the project path on PythonAnywhere
   project_home = '/home/YOUR_PYANYWHERE_USERNAME/YOUR_REPO'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   os.environ['FLASK_ENV'] = 'production'
   # set a secure secret later using the Web tab environment variables
   # os.environ['SECRET_KEY'] = 'set-this-in-web-config'
   from app import app as application
   ```
7. Static files: in the Web tab, add a static file mapping: URL `/static/` -> `/home/YOUR_PYANYWHERE_USERNAME/YOUR_REPO/static`
8. Environment variables: in the Web tab set:
   - `SECRET_KEY` = a secure random string
   - `FLASK_ENV` = `production`
   - (Optional) `DATA_PATH` = `/home/YOUR_PYANYWHERE_USERNAME/YOUR_REPO/data/hostels.xlsx` (if your app reads this env var)
9. Reload the web app from the Web tab.

Alternative: Upload ZIP via Files UI
1. From Windows PowerShell, create an archive without `venv` and `.git` (one way is to copy files to a temp directory, then compress):
   ```powershell
   mkdir ..\deploy_tmp
   robocopy . ..\deploy_tmp /MIR /XD .git venv
   cd ..\deploy_tmp
   Compress-Archive -Path * -DestinationPath ..\hostel_app.zip -Force
   ```
2. In PythonAnywhere Files tab, upload `hostel_app.zip` to your home directory and extract it.
3. Follow steps 5–9 from the GitHub method above (create virtualenv, install requirements, configure WSGI, set static mapping and env vars).

Post-deploy checklist
- Make sure `data/hostels.xlsx` is present and writable by the web process.
- Confirm `static/uploads` exists and is writable (for image uploads).
- Turn `DEBUG = False` in production (either in code or ensure `FLASK_ENV=production`).
- Check logs (Web tab -> error log / server log) for issues.
- If you used relative file paths in `app.py`, verify they're correct for the deployed path.

Troubleshooting tips
- If you get a permissions error writing to `data/hostels.xlsx`, check file ownership/permissions. Use PythonAnywhere "Files" UI to fix or recreate the file.
- If imports fail, ensure the correct Python version and virtualenv with required packages.
- Use the Bash console on PythonAnywhere to run `python -m pip install -r requirements.txt` and `python app.py` for local tests there.

Security notes
- Never commit sensitive secrets to GitHub. Use the PythonAnywhere Web tab to set `SECRET_KEY`.
- Consider migrating from Excel to a proper DB (SQLite / PostgreSQL) for production if the app receives many requests or will be scaled.

If you want, I can:
- Prepare a ready-to-upload minimal WSGI file template added to this repo.
- Create a short `passenger_wsgi.template.py` file you can copy to PythonAnywhere and edit the path.
- Or I can prepare a Git push script for Windows PowerShell that excludes `venv` and other unwanted files.
