# Render Deployment

1. Push this project to a GitHub repository.
2. In Render, create a new Blueprint and select this repository.
3. Render will read `render.yaml`, create a web service, and attach PostgreSQL.
4. Keep `ADMIN_URL` private. The default is `/secure-admin/`.
5. Create a staff user after the first deploy:

```bash
python manage.py createsuperuser
```

Set `BUSINESS_APPROVAL_NOTE` in Render if you need the public dashboard endnote to match your actual registration or license wording.

