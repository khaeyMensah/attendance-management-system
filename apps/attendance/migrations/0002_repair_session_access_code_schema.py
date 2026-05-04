from django.db import migrations



def repair_access_code_column(apps, schema_editor):
    connection = schema_editor.connection
    table = 'attendance_session'

    with connection.cursor() as cursor:
        existing_columns = {
            col.name for col in connection.introspection.get_table_description(cursor, table)
        }
        if 'access_code' not in existing_columns:
            cursor.execute("ALTER TABLE attendance_session ADD COLUMN access_code varchar(8)")

        cursor.execute("SELECT id, access_code FROM attendance_session ORDER BY id")
        rows = cursor.fetchall()
        used_codes = {code for _, code in rows if code}

        for session_id, code in rows:
            if code:
                continue

            candidate = f"S{session_id:07d}"[-8:]
            suffix = 1
            while candidate in used_codes:
                candidate = f"S{(session_id + suffix):07d}"[-8:]
                suffix += 1

            cursor.execute(
                "UPDATE attendance_session SET access_code = %s WHERE id = %s",
                [candidate, session_id],
            )
            used_codes.add(candidate)

        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS attendance_session_access_code_uniq "
            "ON attendance_session(access_code)"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(repair_access_code_column, migrations.RunPython.noop),
    ]
