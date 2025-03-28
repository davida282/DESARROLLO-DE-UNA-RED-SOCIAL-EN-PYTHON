from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Markdown

class PantallaInicio(Screen):
    """Pantalla de inicio de WatchPub."""

    CSS = """
    Button#registro {
        background: blue;
        color: white;
        border: none;
        padding: 1;
        width: 100%;
    }

    Button#registro:hover {
        background: darkblue;
    }

    Button#login {
        background: gray;
        color: white;
        border: none;
        padding: 1;
        width: 100%;
    }

    Button#login:hover {
        background: darkgray;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Markdown("""
# WATCHPUB
""", classes="titulo"),
            Button("📝 Crear cuenta", id="registro"),
            Button("🔑 Iniciar sesión", id="login"),
        )
        yield Footer()

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        if event.button.id == "registro":
            self.app.push_screen("pantalla_registro")  # Ir a la pantalla de registro
        elif event.button.id == "login":
            self.app.push_screen("pantalla_login")  # Ir a la pantalla de inicio de sesión

# Exportar la clase correctamente
__all__ = ["PantallaInicio"]