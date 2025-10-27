"""
Database initialization and management for PostgreSQL.
All data is stored locally on your machine.
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseManager:
    """Manages PostgreSQL database connection and initialization."""

    def __init__(self):
        self.db_name = os.getenv('DB_NAME', 'privacy_deletion_db')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'postgres')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')

    def create_database(self):
        """Create the database if it doesn't exist."""
        try:
            # Connect to PostgreSQL server (default postgres database)
            conn = psycopg2.connect(
                dbname='postgres',
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_name,)
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(self.db_name)
                    )
                )
                print(f"✓ Database '{self.db_name}' created successfully")
            else:
                print(f"✓ Database '{self.db_name}' already exists")

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            print(f"Error creating database: {e}")
            raise

    def get_connection(self):
        """Get a connection to the application database."""
        return psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )

    def initialize_schema(self):
        """Create all necessary tables for the application."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Create accounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id SERIAL PRIMARY KEY,
                    email_address VARCHAR(255) UNIQUE NOT NULL,
                    service VARCHAR(50) NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    domain VARCHAR(255) UNIQUE NOT NULL,
                    company_name VARCHAR(255),
                    privacy_contact VARCHAR(255),
                    contact_type VARCHAR(50) DEFAULT 'email',
                    last_verified DATE,
                    notes TEXT
                )
            ''')

            # Create requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
                    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SENT', 'REPLIED', 'COMPLETED', 'FAILED')),
                    sent_date TIMESTAMP,
                    sent_message_id TEXT,
                    reply_received_date TIMESTAMP,
                    completion_date TIMESTAMP,
                    notes TEXT
                )
            ''')

            # ═══════════════════════════════════════════════════════════════════════
            # NEW FEATURE: Exposed Data Table
            # ═══════════════════════════════════════════════════════════════════════
            # This table stores data exposures found through breach monitoring (HIBP),
            # OSINT scanning (Sherlock, theHarvester), and other privacy scanning tools.
            #
            # Purpose:
            #   - Track breached passwords (via k-anonymity HIBP API)
            #   - Monitor email breaches (via HIBP breachedaccount API)
            #   - Record username exposures (via Sherlock social media scanning)
            #   - Store phone number exposures (future: phoneinfoga integration)
            #
            # Privacy Design:
            #   - Passwords are NEVER stored, only breach status
            #   - All data is local-only (no cloud sync)
            #   - User maintains full control over exposure data
            # ═══════════════════════════════════════════════════════════════════════
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exposed_data (
                    id SERIAL PRIMARY KEY,
                    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
                    data_type VARCHAR(50) NOT NULL CHECK (data_type IN ('email', 'password', 'username', 'phone')),
                    data_value TEXT NOT NULL,
                    source VARCHAR(100) NOT NULL,
                    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('Critical', 'High', 'Medium', 'Low')),
                    details JSONB,
                    status VARCHAR(50) DEFAULT 'EXPOSED' CHECK (status IN ('EXPOSED', 'ACKNOWLEDGED', 'RESOLVED')),
                    found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged_date TIMESTAMP,
                    resolved_date TIMESTAMP
                )
            ''')

            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_companies_domain
                ON companies(domain)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_requests_status
                ON requests(status)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_requests_company
                ON requests(company_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_requests_account
                ON requests(account_id)
            ''')

            # ═══════════════════════════════════════════════════════════════════════
            # NEW FEATURE: Exposed Data Indexes
            # ═══════════════════════════════════════════════════════════════════════
            # Optimize queries for the Exposure Dashboard UI
            # ═══════════════════════════════════════════════════════════════════════
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exposed_data_risk_level
                ON exposed_data(risk_level)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exposed_data_status
                ON exposed_data(status)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exposed_data_account
                ON exposed_data(account_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exposed_data_type
                ON exposed_data(data_type)
            ''')

            conn.commit()
            print("✓ Database schema initialized successfully")
            print("  - accounts table created")
            print("  - companies table created")
            print("  - requests table created")
            print("  - exposed_data table created (NEW)")
            print("  - indexes created")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error initializing schema: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def migrate_progress_tracking(self):
        """
        Add progress tracking columns to existing requests table.

        This migration adds three new columns to support real-time progress updates:
          - progress (0-100): Percentage completion of deletion request workflow
          - current_step: Human-readable description of current operation
          - total_steps: Total number of steps in the workflow (default: 3)

        The migration is idempotent - it checks if columns exist before adding them,
        so it's safe to run multiple times without errors.

        Workflow Steps:
          1. Send deletion request email
          2. Await company response
          3. Confirm deletion completed
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            print("\n" + "="*60)
            print("RUNNING MIGRATION: Progress Tracking for Requests")
            print("="*60)

            # Check if columns already exist to avoid errors
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'requests'
                AND column_name IN ('progress', 'current_step', 'total_steps')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]

            migrations_applied = []

            # Add 'progress' column if it doesn't exist
            if 'progress' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE requests
                    ADD COLUMN progress INT DEFAULT 0
                    CHECK (progress >= 0 AND progress <= 100)
                """)
                migrations_applied.append("progress column")
                print("  ✓ Added 'progress' column (0-100 percentage)")
            else:
                print("  ⊙ 'progress' column already exists (skipping)")

            # Add 'current_step' column if it doesn't exist
            if 'current_step' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE requests
                    ADD COLUMN current_step VARCHAR(100)
                """)
                migrations_applied.append("current_step column")
                print("  ✓ Added 'current_step' column (workflow status)")
            else:
                print("  ⊙ 'current_step' column already exists (skipping)")

            # Add 'total_steps' column if it doesn't exist
            if 'total_steps' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE requests
                    ADD COLUMN total_steps INT DEFAULT 3
                """)
                migrations_applied.append("total_steps column")
                print("  ✓ Added 'total_steps' column (default: 3)")
            else:
                print("  ⊙ 'total_steps' column already exists (skipping)")

            # Initialize progress for existing records
            if migrations_applied:
                cursor.execute("""
                    UPDATE requests
                    SET progress = CASE
                        WHEN status = 'COMPLETED' THEN 100
                        WHEN status = 'REPLIED' THEN 66
                        WHEN status = 'SENT' THEN 33
                        ELSE 0
                    END,
                    current_step = CASE
                        WHEN status = 'COMPLETED' THEN 'Deletion confirmed'
                        WHEN status = 'REPLIED' THEN 'Awaiting confirmation'
                        WHEN status = 'SENT' THEN 'Request sent, awaiting reply'
                        WHEN status = 'FAILED' THEN 'Request failed'
                        ELSE 'Pending'
                    END
                    WHERE progress IS NULL OR current_step IS NULL
                """)
                updated_count = cursor.rowcount
                if updated_count > 0:
                    print(f"  ✓ Initialized progress for {updated_count} existing requests")

            conn.commit()

            print("="*60)
            if migrations_applied:
                print(f"✓ Migration completed: {', '.join(migrations_applied)}")
            else:
                print("✓ Migration already applied (no changes needed)")
            print("="*60 + "\n")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"\n✗ Migration failed: {e}\n")
            raise
        finally:
            cursor.close()
            conn.close()

    def run_all_migrations(self):
        """
        Run all database migrations in order.

        This function ensures the database schema is up-to-date with all new features.
        It's safe to run multiple times - migrations are idempotent.

        Current migrations:
          1. Progress tracking columns for requests table
        """
        print("\n" + "="*60)
        print("CHECKING FOR DATABASE MIGRATIONS")
        print("="*60)

        try:
            # Migration 1: Progress tracking
            self.migrate_progress_tracking()

            print("="*60)
            print("✓ All migrations completed successfully")
            print("="*60 + "\n")

        except Exception as e:
            print("\n" + "="*60)
            print("✗ Migration process encountered an error")
            print("="*60)
            print(f"Error: {e}\n")
            raise


def initialize_database():
    """Main function to set up the database."""
    print("\n" + "="*50)
    print("PRIVACY DATA DELETION TOOL - Database Setup")
    print("="*50)
    print("\nInitializing local PostgreSQL database...")
    print("All data will be stored locally on your machine.\n")

    try:
        db_manager = DatabaseManager()

        # Create database if it doesn't exist
        db_manager.create_database()

        # Create tables and schema
        db_manager.initialize_schema()

        # Run all database migrations for new features
        print("\nChecking for schema updates...")
        db_manager.run_all_migrations()

        print("\n" + "="*50)
        print("✓ Database setup completed successfully!")
        print("="*50)
        print("\nConnection details:")
        print(f"  Database: {db_manager.db_name}")
        print(f"  Host: {db_manager.db_host}")
        print(f"  Port: {db_manager.db_port}")
        print(f"  User: {db_manager.db_user}")
        print("\n")

    except Exception as e:
        print("\n" + "="*50)
        print("✗ Database setup failed!")
        print("="*50)
        print(f"\nError: {e}")
        print("\nPlease ensure PostgreSQL is running and credentials are correct.")
        print("You can configure database settings in a .env file:")
        print("  DB_NAME=privacy_deletion_db")
        print("  DB_USER=postgres")
        print("  DB_PASSWORD=your_password")
        print("  DB_HOST=localhost")
        print("  DB_PORT=5432")
        raise


if __name__ == "__main__":
    initialize_database()
