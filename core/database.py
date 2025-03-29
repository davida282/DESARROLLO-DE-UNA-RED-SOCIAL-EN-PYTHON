import firebase_admin
from firebase_admin import credentials, db
from typing import Any, Dict, Optional

class FirebaseDB:
    def __init__(self, credential_path: str, database_url: str):
        if not firebase_admin._apps:
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred, {'databaseURL': database_url})

    def write(self, path: str, data: Dict[str, Any]) -> None:
        try:
            db.reference(path).set(data)
        except Exception as e:
            raise Exception(f"Error writing to {path}: {e}")

    def read(self, path: str) -> Optional[Dict[str, Any]]:
        try:
            return db.reference(path).get()
        except Exception as e:
            raise Exception(f"Error reading from {path}: {e}")

    def push(self, path: str, data: Dict[str, Any]) -> str:
        try:
            ref = db.reference(path).push()
            ref.set(data)
            return ref.key
        except Exception as e:
            raise Exception(f"Error pushing to {path}: {e}")

    def update(self, path: str, data: Dict[str, Any]) -> None:
        try:
            db.reference(path).update(data)
        except Exception as e:
            raise Exception(f"Error updating {path}: {e}")

    def delete(self, path: str) -> None:
        try:
            db.reference(path).delete()
        except Exception as e:
            raise Exception(f"Error deleting {path}: {e}")

db_instance = FirebaseDB(
    "/home/camper/Documentos/Red Social/DESARROLLO-DE-UNA-RED-SOCIAL-EN-PYTHON/credentials.json",  # Reemplazar con la ruta real
    "https://red-social-python-default-rtdb.firebaseio.com/"
)