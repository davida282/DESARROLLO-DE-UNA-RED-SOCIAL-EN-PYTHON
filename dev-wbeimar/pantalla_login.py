import firebase_admin
from firebase_admin import credentials, db
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label
from mi_perfil import MiPerfil  # Importar la pantalla de perfil

# Inicializar Firebase con Realtime Database solo si no está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate("dev-wbeimar/registroususarios-94b03-firebase-adminsdk-fbsvc-0549e88d91.json")  # Ruta exacta
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://registroususarios-94b03-default-rtdb.firebaseio.com/'
    })

class PantallaLogin(Screen):  # Cambio de nombre
    """Pantalla de inicio de sesión para WatchPub."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("## Iniciar Sesión", classes="titulo"),
            Input(placeholder="Nombre de usuario", id="usuario"),
            Input(placeholder="Contraseña", password=True, id="password"),
            Button("✅ Iniciar sesión", id="login"),
            Button("⬅ Volver", id="volver"),
            Label("", id="mensaje")  # Mensaje de feedback
        )
        yield Footer()

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        mensaje = self.query_one("#mensaje", Label)
        usuario_input = self.query_one("#usuario", Input)
        password_input = self.query_one("#password", Input)
        
        if event.button.id == "login":
            usuario = usuario_input.value.strip()
            password = password_input.value.strip()
            
            if usuario and password:
                try:
                    ref = db.reference(f"usuarios/{usuario}").get()
                    if ref:
                        if ref.get("password") == password:
                            mensaje.update("✅ Ingresando...")
                            self.app.log("✅ Ingresando...")
                            self.app.push_screen(MiPerfil(usuario))  # Redirigir al perfil
                        else:
                            mensaje.update("❌ Contraseña incorrecta.")
                            self.app.log("❌ Contraseña incorrecta.")
                    else:
                        mensaje.update("❌ Usuario no encontrado en la base de datos.")
                        self.app.log("❌ Usuario no encontrado en la base de datos.")
                except Exception as e:
                    mensaje.update(f"❌ Error: {e}")
                    self.app.log(f"❌ Error: {e}")
            else:
                mensaje.update("⚠️ Por favor, completa todos los campos.")
                self.app.log("⚠️ Por favor, completa todos los campos.")
            
            # Limpiar los campos de entrada después de intentar iniciar sesión
            usuario_input.value = ""
            password_input.value = ""
        
        elif event.button.id == "volver":
            self.app.pop_screen()  # Regresa al menú principal