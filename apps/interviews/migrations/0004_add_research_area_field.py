# Migration to add research_area field to MockInterviewSession if it doesn't exist

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0003_initial'),
        ('publications', '0007_populate_research_areas_by_department'),
    ]

    operations = [
        # Check if research_area column exists, if not add it
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                -- Check if research_area_id column exists
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'interview_sessions'
                    AND column_name = 'research_area_id'
                ) THEN
                    -- Add the research_area_id column
                    ALTER TABLE interview_sessions
                    ADD COLUMN research_area_id bigint;

                    -- Add foreign key constraint
                    ALTER TABLE interview_sessions
                    ADD CONSTRAINT interview_sessions_research_area_id_fk
                    FOREIGN KEY (research_area_id)
                    REFERENCES research_areas(id)
                    ON DELETE SET NULL;

                    -- Add index for performance
                    CREATE INDEX IF NOT EXISTS interview_sessions_research_area_id_idx
                    ON interview_sessions(research_area_id);
                END IF;
            END
            $$;
            """,
            reverse_sql="""
            DO $$
            BEGIN
                -- Drop the column if it exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'interview_sessions'
                    AND column_name = 'research_area_id'
                ) THEN
                    ALTER TABLE interview_sessions DROP COLUMN research_area_id;
                END IF;
            END
            $$;
            """,
        ),
    ]