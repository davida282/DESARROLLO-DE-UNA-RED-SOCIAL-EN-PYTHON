from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label
import firebase_admin
from firebase_admin import db
from visitar_perfil import VisitarPerfil

class MiPerfil(Screen):
    """Pantalla de perfil del usuario en WatchPub."""

    CSS = """
    Button#publicar {
        background: green;
        color: white;
        border: none;
        padding: 1;
        width: 100%;
    }

    Button#publicar:hover {
        background: darkgreen;
    }

    Button#buscar {
        background: blue;
        color: white;
        border: none;
        padding: 1;
        width: 100%;
    }

    Button#buscar:hover {
        background: darkblue;
    }

    Button#salir {
        background: gray;
        color: white;
        border: none;
        padding: 1;
        width: 100%;
    }

    Button#salir:hover {
        background: darkgray;
    }
    """

    def __init__(self, usuario: str):
        super().__init__()
        self.usuario = usuario  # Guardar el nombre de usuario
        self.publicaciones = []  # Lista para mostrar publicaciones

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"## Perfil de {self.usuario}", classes="titulo"),
            Input(placeholder="Escribe tu publicación...", id="publicacion"),
            Button("📢 Publicar", id="publicar"),
            Static("", id="lista_publicaciones"),  # Área donde se mostrarán las publicaciones
            Input(placeholder="Buscar usuario...", id="buscar_usuario"),
            Button("🔍 Buscar", id="buscar"),
            Button("🚪 Salir", id="salir"),  # Cambiado de "Volver" a "Salir"
            Label("", id="mensaje")  # Mensaje de feedback
        )
        yield Footer()

    def on_mount(self):
        """Carga las publicaciones después de que la pantalla esté completamente construida."""
        self.cargar_publicaciones()

    def cargar_publicaciones(self):
        """Carga publicaciones desde la base de datos y las muestra."""
        publicaciones_ref = db.reference(f"usuarios/{self.usuario}/publicaciones").get()
        if publicaciones_ref:
            self.publicaciones = list(publicaciones_ref.values())
        lista_publicaciones = self.query_one("#lista_publicaciones", Static)
        lista_publicaciones.update("\n".join(self.publicaciones) if self.publicaciones else "No hay publicaciones.")

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        mensaje = self.query_one("#mensaje", Label)
        publicacion_input = self.query_one("#publicacion", Input)
        buscar_input = self.query_one("#buscar_usuario", Input)
        lista_publicaciones = self.query_one("#lista_publicaciones", Static)

        self.app.log(f"🔘 Botón presionado: {event.button.id}")
        mensaje.update(f"🔘 Botón presionado: {event.button.id}")
        self.refresh()

        if event.button.id == "publicar":
            texto = publicacion_input.value.strip()
            if texto:
                mensaje.update("✅ Publicación enviada.")
                self.app.log(f"✅ Publicación de {self.usuario}: {texto}")
                publicacion_input.value = ""  # Limpiar el campo después de publicar

                # Guardar publicación en la base de datos
                publicaciones_ref = db.reference(f"usuarios/{self.usuario}/publicaciones")
                publicaciones_ref.push(texto)

                # Mostrar la publicación en pantalla
                self.publicaciones.append(texto)
                lista_publicaciones.update("\n".join(self.publicaciones))
            else:
                mensaje.update("⚠️ Escribe algo antes de publicar.")
                self.app.log("⚠️ Intento de publicación vacía.")
            self.refresh()

        elif event.button.id == "buscar":
            usuario_a_buscar = buscar_input.value.strip()
            self.app.log(f"🔍 Intentando buscar: {usuario_a_buscar}")
            mensaje.update(f"🔍 Intentando buscar: {usuario_a_buscar}")
            self.refresh()

            if usuario_a_buscar:
                try:
                    ref = db.reference(f"usuarios/{usuario_a_buscar}").get()
                    if ref:
                        mensaje.update("✅ Ingresando al perfil...")
                        self.app.log("✅ Ingresando al perfil...")
                        buscar_input.value = ""  # Limpiar el campo después de la búsqueda
                        self.refresh()
                        self.app.push_screen(VisitarPerfil(self.usuario, usuario_a_buscar))  # Se pasan ambos usuarios correctamente
                    else:
                        mensaje.update("❌ Usuario no encontrado en la base de datos.")
                        self.app.log("❌ Usuario no encontrado en la base de datos.")
                        self.refresh()
                except Exception as e:
                    mensaje.update(f"❌ Error: {e}")
                    self.app.log(f"❌ Error: {e}")
                    self.refresh()
            else:
                mensaje.update("⚠️ Por favor, completa el campo de búsqueda.")
                self.app.log("⚠️ Intento de búsqueda vacía.")
                self.refresh()

        elif event.button.id == "salir":
            self.app.exit()  # Cierra la aplicación y regresa al menú principal

# Exportar la clase correctamente
__all__ = ["MiPerfil"]