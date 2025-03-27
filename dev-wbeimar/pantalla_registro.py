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
        input_usuario = self.query_one("#usuario", Input)
        input_password = self.query_one("#password", Input)

        if event.button.id == "registrar":
            usuario = input_usuario.value.strip().lower()  # Convertir a minúsculas
            password = input_password.value.strip()

            if usuario and password:
                try:
                    ref = db.reference(f"usuarios/{usuario}").get()
                    if ref:
                        mensaje.update("❌ El usuario ya existe. Elige otro nombre.")
                        self.app.log("❌ Intento de registro con un usuario ya existente.")
                    else:
                        db.reference(f"usuarios/{usuario}").set({
                            "usuario": usuario,
                            "password": password  # En producción, usa hashing para la contraseña
                        })
                        mensaje.update("✅ Usuario registrado exitosamente.")
                        self.app.log(f"✅ Usuario '{usuario}' registrado en la base de datos.")
                except Exception as e:
                    mensaje.update(f"❌ Error: {e}")
                    self.app.log(f"❌ Error: {e}")
            else:
                mensaje.update("⚠️ Por favor, completa todos los campos.")
                self.app.log("⚠️ Por favor, completa todos los campos.")

            # Borrar los campos después de presionar "Registrar"
            input_usuario.value = ""
            input_password.value = ""
        
        elif event.button.id == "volver":
            self.app.pop_screen()  # Regresa al menú principal
