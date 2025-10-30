# Migration to fix ResearchArea table conflict by renaming interviews.ResearchArea table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0003_add_research_area_model'),
    ]

    operations = [
        # First, check if the table exists and handle the conflict
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                -- Check if the table exists and has the right structure for interviews
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'research_areas') THEN
                    -- Check if it's the interviews version (has is_active column)
                    IF EXISTS (SELECT 1 FROM information_schema.columns
                              WHERE table_name = 'research_areas' AND column_name = 'is_active') THEN
                        -- Rename it to avoid conflict
                        ALTER TABLE research_areas RENAME TO interview_research_areas;
                    END IF;
                END IF;

                -- If the table doesn't exist, create it with the correct name
                IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'interview_research_areas') THEN
                    CREATE TABLE interview_research_areas (
                        id bigserial PRIMARY KEY,
                        name character varying(200) UNIQUE NOT NULL,
                        description text,
                        is_active boolean DEFAULT true NOT NULL,
                        created_at timestamp with time zone DEFAULT now() NOT NULL
                    );
                    CREATE INDEX interview_research_areas_name_idx ON interview_research_areas(name);
                END IF;
            END
            $$;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS interview_research_areas;
            """,
        ),
    ]