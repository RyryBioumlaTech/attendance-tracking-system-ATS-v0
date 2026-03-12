from app.models import User, db
import os

def create_default_admin():
    if User.query.first() is None:  # Vérifie si la table est vide
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_password:
            raise ValueError("Le mot de passe admin doit être défini dans la variable d'environnement ADMIN_PASSWORD")

        # The User.name column is non-nullable, so we must supply some value here.
        # Use the email local-part or a generic label if none provided.
        default_name = os.getenv("ADMIN_NAME", "Administrator")
        default_surname = os.getenv("ADMIN_SURNAME", "")

        admin = User(
            name=default_name,
            surname=default_surname,
            email=admin_email,
            role='superAd'
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print("Admin par défaut créé avec succès")