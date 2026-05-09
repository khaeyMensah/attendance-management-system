# attendance-management-system

## Deployment and database schema management

Use Django migrations for every database schema change, commit the generated migration files, and run migrations as part of deployment.

Recommended deployment sequence for Render or similar hosts:

```bash
pip install -r requirements.txt
npm install --prefix theme/static_src
npm run build --prefix theme/static_src
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

If your hosting platform supports a release phase, put `python manage.py migrate --noinput` there so your schema changes are applied after the code is released.

Avoid manual production schema changes unless a one-time repair is necessary.
