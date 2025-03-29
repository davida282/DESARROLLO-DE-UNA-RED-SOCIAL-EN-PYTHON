from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label
from core.auth import auth
from screens.mural import Mural  # Cambiado de Perfil a Mural

class Login(Screen):
    CSS = """
    Button#login { background: green; color: white; border: none; padding: 1; width: 100%; }
    Button#login:hover { background: darkgreen; }
    Button#volver { background: gray; color: white; border: none; padding: 1; width: 100%; }
    Button#volver:hover { background: darkgray; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("## Iniciar Sesión", classes="titulo"),
            Input(placeholder="Nombre de usuario", id="usuario"),
            Input(placeholder="Contraseña", password=True, id="password"),
            Button("✅ Iniciar sesión", id="login"),
            Button("⬅ Volver", id="volver"),
            Label("", id="mensaje")
        )
        yield Footer()

    def on_button_pressed(self, event):
        mensaje = self.query_one("#mensaje", Label)
        usuario = self.query_one("#usuario", Input).value.strip().lower()
        password = self.query_one("#password", Input).value.strip()

        if event.button.id == "login":
            if not usuario or not password:
                mensaje.update("⚠️ Completa todos los campos.")
            elif auth.login(usuario, password):
                mensaje.update("✅ Ingresando...")
                self.app.push_screen(Mural(auth.get_current_user()))  # Cambiado de Perfil a Mural
            else:
                mensaje.update("❌ Credenciales incorrectas.")
            self.query_one("#usuario", Input).value = ""
            self.query_one("#password", Input).value = ""
        elif event.button.id == "volver":
            self.app.pop_screen()