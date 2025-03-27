import firebase_admin
from firebase_admin import db
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, Label

class VisitarPerfil(Screen):
    """Pantalla para visitar el perfil de otro usuario en WatchPub."""
    
    def __init__(self, usuario_actual: str, usuario_a_visitar: str):
        super().__init__()
        self.usuario_actual = usuario_actual  # Guardar el usuario que inició sesión
        self.usuario_a_visitar = usuario_a_visitar  # Usuario que se está visitando
        self.publicaciones = []  # Lista de publicaciones del usuario visitado

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("", id="titulo"),
            Label("", id="mensaje"),  # Mensaje de feedback
            Static("", id="lista_publicaciones"),  # Donde se mostrarán las publicaciones
            Button("⬅ Volver a mi perfil", id="volver_perfil"),
        )
        yield Footer()

    def on_mount(self):
        """Verifica si el usuario existe en la base de datos al abrir la pantalla."""
        mensaje = self.query_one("#mensaje", Label)
        titulo = self.query_one("#titulo", Static)
        lista_publicaciones = self.query_one("#lista_publicaciones", Static)
        
        ref = db.reference(f"usuarios/{self.usuario_a_visitar}").get()
        
        if ref:
            titulo.update(f"## Perfil de {self.usuario_a_visitar}")
            mensaje.update(f"✅ Perfil de {self.usuario_a_visitar} encontrado.")
            self.app.log(f"✅ Perfil de {self.usuario_a_visitar} encontrado en la base de datos.")
            
            # Cargar publicaciones del usuario visitado
            publicaciones_ref = db.reference(f"usuarios/{self.usuario_a_visitar}/publicaciones").get()
            if publicaciones_ref:
                self.publicaciones = list(publicaciones_ref.values())
                lista_publicaciones.update("\n".join(self.publicaciones))
            else:
                lista_publicaciones.update("No hay publicaciones.")
        else:
            mensaje.update("❌ Usuario no encontrado. Permaneciendo en tu perfil.")
            self.app.log("❌ Usuario no encontrado en la base de datos.")
            self.app.pop_screen()  # Si no existe, volver al perfil actual

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        if event.button.id == "volver_perfil":
            from mi_perfil import MiPerfil  # Importación diferida para evitar import circular
            self.app.push_screen(MiPerfil(self.usuario_actual))  # Regresa al perfil principal

# Exportar la clase correctamente
__all__ = ["VisitarPerfil"]