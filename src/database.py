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

            conn.commit()
            print("✓ Database schema initialized successfully")
            print("  - accounts table created")
            print("  - companies table created")
            print("  - requests table created")
            print("  - indexes created")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error initializing schema: {e}")
            raise
        finally:
            cursor.close()
            conn.close()


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
