import os
import sqlite3

def clean_database():
    """Remove and recreate the database."""
    db_path = os.path.join('data', 'robosite.db')
    
    # Remove existing database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database at {db_path}")
        except Exception as e:
            print(f"Error removing database: {str(e)}")
            return
    
    print("Database cleaned successfully. Run server.py to initialize a fresh database.")

def list_secrets(project_id: str) -> None:
    """
    List all secrets in the given project.
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the parent project.
    parent = f"projects/{project_id}"

    # List all secrets.
    for secret in client.list_secrets(request={"parent": parent}):
        print(f"Found secret: {secret.name}")

if __name__ == "__main__":
    clean_database()
    #list_secrets("robosite-462417")


