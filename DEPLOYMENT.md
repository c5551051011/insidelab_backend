# InsideLab Deployment Guide

This guide explains how to deploy InsideLab from development to production using the separated environment configuration.

## 🏗️ Environment Structure

InsideLab now uses a separated settings structure:

```
insidelab/settings/
├── __init__.py
├── base.py          # Common settings
├── development.py   # Development-specific settings
└── production.py    # Production-specific settings
```

## 🔧 Environment Variables

### Required Environment Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `DJANGO_ENVIRONMENT` | `development` | `production` | Environment selector |
| `SECRET_KEY` | ✅ | ✅ | Django secret key |
| `DB_PASSWORD` | ✅ | - | Development DB password |
| `PROD_DB_PASSWORD` | - | ✅ | Production DB password |

### Complete Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Environment
DJANGO_ENVIRONMENT=development  # or production

# Database (Development)
DB_NAME=postgres
DB_USER=postgres.your-dev-project-id
DB_PASSWORD=your-dev-password
DB_HOST=aws-0-ap-northeast-2.pooler.supabase.com
DB_PORT=5432

# Database (Production)
PROD_DB_NAME=postgres
PROD_DB_USER=postgres.your-prod-project-id
PROD_DB_PASSWORD=your-prod-password
PROD_DB_HOST=aws-0-ap-northeast-2.pooler.supabase.com
PROD_DB_PORT=5432

# Email
RESEND_API_KEY=re_your_api_key
DEFAULT_FROM_EMAIL=InsideLab <noreply@insidelab.io>

# Site
SITE_DOMAIN=localhost:8000  # or insidelab.io for production
```

## 🚀 Deployment Process

### Step 1: Prepare Production Database

1. **Create New Supabase Database**
   ```bash
   # Go to Supabase Dashboard
   # Create new project for production
   # Note down the connection details
   ```

2. **Update Environment Variables**
   ```bash
   # In your production environment (Railway/Heroku/etc.)
   DJANGO_ENVIRONMENT=production
   PROD_DB_NAME=postgres
   PROD_DB_USER=postgres.your-prod-project-id
   PROD_DB_PASSWORD=your-prod-password
   PROD_DB_HOST=aws-0-ap-northeast-2.pooler.supabase.com
   PROD_DB_PORT=5432
   ```

### Step 2: Export Schema from Development

```bash
# Run the deployment preparation script
python scripts/deploy_to_production.py

# This will:
# 1. Generate migration files
# 2. Export SQL schema
# 3. Create production_schema.sql
```

### Step 3: Deploy to Production

```bash
# Set production environment
export DJANGO_ENVIRONMENT=production

# Apply migrations to production database
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Populate academic venues
python scripts/populate_all_venues.py

# Collect static files (if using static file serving)
python manage.py collectstatic --noinput
```

### Step 4: Verify Production Deployment

```bash
# Check system configuration
python manage.py check

# Test database connection
python manage.py dbshell

# Verify API endpoints
curl https://your-production-domain.com/api/v1/universities/
```

## 🔍 Environment Detection

The system automatically detects the environment using the `DJANGO_ENVIRONMENT` variable:

```python
# manage.py and wsgi.py automatically select:
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    # Use production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings.production')
else:
    # Use development settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings.development')
```

## 📊 Database Migration Strategy

### Schema-Only Migration (Recommended)

This approach migrates only the database structure, not the data:

1. **Development**: Contains your current data and schema
2. **Production**: Gets only the schema (tables, indexes, constraints)
3. **Benefits**: Clean production start, no data conflicts

### If You Need Data Migration

If you need to migrate specific data (like venue classifications):

```bash
# Export specific data
python manage.py dumpdata publications.Venue --output=venues.json

# Import to production
python manage.py loaddata venues.json
```

## 🛠️ Local Development

Continue developing locally with:

```bash
# Default uses development settings
python manage.py runserver

# Or explicitly
DJANGO_ENVIRONMENT=development python manage.py runserver
```

## 🔐 Security Considerations

### Production Security Features

- ✅ `DEBUG=False`
- ✅ Strict CORS policy
- ✅ HTTPS enforcement
- ✅ Security headers
- ✅ Separate database credentials
- ✅ Environment isolation

### Environment Isolation

- Development and production use completely separate databases
- Different cache configurations
- Separate email configurations
- Different allowed hosts and CORS origins

## 🐛 Troubleshooting

### Common Issues

1. **Migration Errors**
   ```bash
   # Check migration status
   python manage.py showmigrations

   # Apply specific migration
   python manage.py migrate app_name migration_name
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   python manage.py dbshell

   # Check settings
   python manage.py diffsettings
   ```

3. **Environment Variables**
   ```bash
   # Check current environment
   python -c "import os; print('Environment:', os.environ.get('DJANGO_ENVIRONMENT', 'development'))"
   ```

### Getting Help

- Check Django logs: `tail -f logs/django.log`
- Database logs: Check Supabase dashboard
- Application logs: Check Railway/hosting platform logs

## 📝 Deployment Checklist

### Before Deployment
- [ ] ✅ New production database created
- [ ] ✅ Environment variables configured
- [ ] ✅ Production domain configured
- [ ] ✅ Email service configured (Resend)
- [ ] ✅ Redis configured (optional)

### During Deployment
- [ ] ✅ Migrations applied successfully
- [ ] ✅ Static files collected
- [ ] ✅ Superuser created
- [ ] ✅ Venues populated

### After Deployment
- [ ] ✅ API endpoints working
- [ ] ✅ Authentication working
- [ ] ✅ Email sending working
- [ ] ✅ Database queries working
- [ ] ✅ Frontend can connect

## 🎯 Next Steps

After successful deployment:

1. **Monitor Performance**: Set up logging and monitoring
2. **Backup Strategy**: Configure automated database backups
3. **SSL Certificate**: Ensure HTTPS is properly configured
4. **Domain Setup**: Configure custom domain if needed
5. **CI/CD**: Set up automated deployment pipeline

---

**Need Help?** Check the troubleshooting section or create an issue in the repository.