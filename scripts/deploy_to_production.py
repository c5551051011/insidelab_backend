#!/usr/bin/env python
"""
Production Deployment Script for InsideLab
This script helps deploy database schema from development to production.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step, description):
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 40)

def run_command(command, description=""):
    """Run a command and return success status"""
    if description:
        print(f"Running: {description}")

    print(f"Command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print("❌ Failed!")
        if result.stderr:
            print("Error:", result.stderr)
        if result.stdout:
            print("Output:", result.stdout)
        return False

def main():
    print_header("InsideLab Production Deployment")

    print("This script will help you deploy your database schema to production.")
    print("Make sure you have:")
    print("1. ✅ Created a new Supabase production database")
    print("2. ✅ Set up production environment variables")
    print("3. ✅ Backed up your development database")
    print()

    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Error: manage.py not found. Please run this script from the Django project root.")
        sys.exit(1)

    # Ask for confirmation
    response = input("Are you ready to proceed? (y/N): ")
    if response.lower() != 'y':
        print("Deployment cancelled.")
        sys.exit(0)

    print_step(1, "Export Development Database Schema")
    print("We'll generate SQL schema from your development database...")

    # Generate migration files
    if not run_command("python manage.py makemigrations", "Generate any pending migrations"):
        print("Please fix migration issues before continuing.")
        return

    # Export schema using Django's sqlmigrate
    print("\\nExporting database schema...")

    # Get list of apps with migrations
    apps = ['authentication', 'labs', 'publications', 'reviews', 'universities', 'utils']

    schema_file = "production_schema.sql"
    with open(schema_file, 'w') as f:
        f.write("-- InsideLab Production Database Schema\\n")
        f.write("-- Generated automatically from Django migrations\\n\\n")

        for app in apps:
            print(f"Exporting {app} migrations...")

            # Get migration files for this app
            migration_dir = Path(f"apps/{app}/migrations")
            if migration_dir.exists():
                migration_files = sorted([f.stem for f in migration_dir.glob("*.py") if f.stem != "__init__"])

                for migration in migration_files:
                    if migration.startswith("0"):  # Only numbered migrations
                        result = subprocess.run(
                            f"python manage.py sqlmigrate {app} {migration}",
                            shell=True, capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            f.write(f"-- Migration: {app}.{migration}\\n")
                            f.write(result.stdout)
                            f.write("\\n\\n")

    print(f"✅ Schema exported to {schema_file}")

    print_step(2, "Prepare Production Environment")
    print("Next steps for production deployment:")
    print()
    print("1. 📋 Copy your production database credentials:")
    print("   - Supabase Project URL")
    print("   - Database password")
    print("   - Connection details")
    print()
    print("2. 🔧 Set environment variables in your production environment:")
    print("   DJANGO_ENVIRONMENT=production")
    print("   PROD_DB_NAME=postgres")
    print("   PROD_DB_USER=postgres.your-prod-project")
    print("   PROD_DB_PASSWORD=your-prod-password")
    print("   PROD_DB_HOST=aws-0-ap-northeast-2.pooler.supabase.com")
    print("   PROD_DB_PORT=5432")
    print()

    print_step(3, "Run Migrations on Production")
    print("To apply the schema to production, run these commands:")
    print()
    print("# Set production environment")
    print("export DJANGO_ENVIRONMENT=production")
    print()
    print("# Run migrations")
    print("python manage.py migrate")
    print()
    print("# Create superuser (optional)")
    print("python manage.py createsuperuser")
    print()
    print("# Populate venues (recommended)")
    print("python scripts/populate_all_venues.py")
    print()

    print_step(4, "Verify Production Setup")
    print("After deployment, verify these work:")
    print("- ✅ Database connections")
    print("- ✅ API endpoints")
    print("- ✅ Authentication")
    print("- ✅ Email sending")
    print()

    print_header("Deployment Preparation Complete!")
    print(f"📄 Schema file created: {schema_file}")
    print("🚀 Follow the steps above to complete production deployment.")
    print()
    print("Need help? Check the deployment documentation or contact support.")

if __name__ == "__main__":
    main()