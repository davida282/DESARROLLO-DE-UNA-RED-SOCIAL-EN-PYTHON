import firebase_admin
from firebase_admin import credentials, db
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label

# Inicializar Firebase con Realtime Database
cred = credentials.Certificate("dev-wbeimar/registroususarios-94b03-firebase-adminsdk-fbsvc-0549e88d91.json")  # Ruta exacta
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://registroususarios-94b03-default-rtdb.firebaseio.com/'
})

class PantallaRegistro(Screen):  # Cambio de nombre
    """Pantalla de registro de usuario para WatchPub."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("## Crear Cuenta", classes="titulo"),
            Input(placeholder="Nombre de usuario", id="usuario"),
            Input(placeholder="Contraseña", password=True, id="password"),
            Button("✅ Registrar", id="registrar"),
            Button("⬅ Volver", id="volver"),
            Label("", id="mensaje")  # Mensaje de feedback
        )
        yield Footer()

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        mensaje = self.query_one("#mensaje", Label)
        
        if event.button.id == "registrar":
            usuario = self.query_one("#usuario", Input).value
            password = self.query_one("#password", Input).value
            
            if usuario and password:
                try:
                    ref = db.reference("usuarios/")
                    ref.child(usuario).set({
                        "usuario": usuario,
                        "password": password  # Nota: En producción, hashea la contraseña
                    })
                    mensaje.update("✅ Usuario registrado exitosamente en Realtime Database.")
                    self.app.log("✅ Usuario registrado exitosamente en Realtime Database.")
                except Exception as e:
                    mensaje.update(f"❌ Error: {e}")
                    self.app.log(f"❌ Error: {e}")
            else:
                mensaje.update("⚠️ Por favor, completa todos los campos.")
                self.app.log("⚠️ Por favor, completa todos los campos.")
        elif event.button.id == "volver":
            self.app.pop_screen()  # Regresa al menú principal
