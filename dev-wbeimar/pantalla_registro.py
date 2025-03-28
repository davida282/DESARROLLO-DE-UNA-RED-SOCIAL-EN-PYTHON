from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label
from firebase_admin import db


class PantallaRegistro(Screen):
    """Pantalla de registro de usuario para WatchPub."""

    CSS = """
    Button#crear_cuenta {
        background: green;
        color: white;
        border: none;
        padding: 1;
        width: 100%;
    }

    Button#crear_cuenta:hover {
        background: darkgreen;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("## Crear Cuenta", classes="titulo"),
            Input(placeholder="Nombre de usuario", id="usuario"),
            Input(placeholder="Contraseña", password=True, id="password"),
            Button("✅ Crear Cuenta", id="crear_cuenta"),
            Button("⬅ Volver", id="volver"),
            Label("", id="mensaje")  # Mensaje de feedback
        , id="formulario")
        yield Footer()

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        mensaje = self.query_one("#mensaje", Label)
        input_usuario = self.query_one("#usuario", Input)
        input_password = self.query_one("#password", Input)

        if event.button.id == "crear_cuenta":
            usuario = input_usuario.value.strip().lower()
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
                            "password": password
                        })
                        mensaje.update("✅ Usuario registrado exitosamente.")
                        self.app.log(f"✅ Usuario '{usuario}' registrado en la base de datos.")
                except Exception as e:
                    mensaje.update(f"❌ Error: {e}")
                    self.app.log(f"❌ Error: {e}")
            else:
                mensaje.update("⚠️ Por favor, completa todos los campos.")
                self.app.log("⚠️ Por favor, completa todos los campos.")

            input_usuario.value = ""
            input_password.value = ""

        elif event.button.id == "volver":
            self.app.pop_screen()