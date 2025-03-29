from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Markdown

class Inicio(Screen):
    CSS = """
    Button#registro { background: blue; color: white; border: none; padding: 1; width: 100%; }
    Button#registro:hover { background: darkblue; }
    Button#login { background: gray; color: white; border: none; padding: 1; width: 100%; }
    Button#login:hover { background: darkgray; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Markdown("# WATCHPUB\nBienvenido a la red social", classes="titulo"),
            Button("📝 Crear cuenta", id="registro"),
            Button("🔑 Iniciar sesión", id="login"),
        )
        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "registro":
            self.app.push_screen("registro")
        elif event.button.id == "login":
            self.app.push_screen("login")