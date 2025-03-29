from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label
from core.auth import auth

class Registro(Screen):
    CSS = """
    Button#crear_cuenta { background: green; color: white; border: none; padding: 1; width: 100%; }
    Button#crear_cuenta:hover { background: darkgreen; }
    Button#volver { background: gray; color: white; border: none; padding: 1; width: 100%; }
    Button#volver:hover { background: darkgray; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("## Crear Cuenta", classes="titulo"),
            Input(placeholder="Nombre de usuario", id="usuario"),
            Input(placeholder="Contraseña (mínimo 6 caracteres)", password=True, id="password"),
            Button("✅ Crear Cuenta", id="crear_cuenta"),
            Button("⬅ Volver", id="volver"),
            Label("", id="mensaje")
        )
        yield Footer()

    def on_button_pressed(self, event):
        mensaje = self.query_one("#mensaje", Label)
        usuario = self.query_one("#usuario", Input).value.strip().lower()
        password = self.query_one("#password", Input).value.strip()

        if event.button.id == "crear_cuenta":
            if not usuario or not password:
                mensaje.update("⚠️ Completa todos los campos.")
            elif len(password) < 6:
                mensaje.update("⚠️ La contraseña debe tener al menos 6 caracteres.")
            elif auth.register(usuario, password):
                mensaje.update("✅ Registro exitoso. Inicia sesión.")
                self.query_one("#usuario", Input).value = ""
                self.query_one("#password", Input).value = ""
            else:
                mensaje.update("❌ El usuario ya existe.")
        elif event.button.id == "volver":
            self.app.pop_screen()