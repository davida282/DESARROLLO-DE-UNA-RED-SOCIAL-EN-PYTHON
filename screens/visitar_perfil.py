from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, Label
from core.database import db_instance

class VisitarPerfil(Screen):
    def __init__(self, usuario_actual: str, usuario_visitado: str):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.usuario_visitado = usuario_visitado

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"## Perfil de {self.usuario_visitado}", id="titulo"),
            Static("", id="publicaciones"),
            Button("⬅ Volver", id="volver"),
            Label("", id="mensaje")
        )
        yield Footer()

    def on_mount(self):
        publicaciones_usuario = db_instance.read(f"usuarios/{self.usuario_visitado}/publicaciones") or {}
        publicaciones_global = db_instance.read("publicaciones") or {}

        if publicaciones_usuario:
            # Eliminar publicaciones huérfanas
            for pub_id in list(publicaciones_usuario.keys()):
                if pub_id not in publicaciones_global:
                    db_instance.delete(f"usuarios/{self.usuario_visitado}/publicaciones/{pub_id}")

            # Volver a leer las publicaciones después de la limpieza
            publicaciones_usuario = db_instance.read(f"usuarios/{self.usuario_visitado}/publicaciones") or {}
            if publicaciones_usuario:
                # Construir el texto con publicaciones y comentarios
                lineas = []
                for pub_id, pub in publicaciones_usuario.items():
                    # Obtener el contenido de la publicación
                    contenido = pub["contenido"] if isinstance(pub, dict) else pub
                    lineas.append(f"Publicación: {contenido}")
                    
                    # Obtener y mostrar los comentarios
                    comentarios = pub.get("comentarios", {}) if isinstance(pub, dict) else {}
                    if comentarios:
                        lineas.append("  Comentarios:")
                        for comentario_id, comentario in comentarios.items():
                            autor = comentario.get("autor", "Anónimo")
                            texto = comentario.get("texto", "")
                            lineas.append(f"    - {autor}: {texto}")
                    else:
                        lineas.append("  (Sin comentarios)")
                    lineas.append("")  # Línea en blanco para separar publicaciones

                texto_publicaciones = "\n".join(lineas)
            else:
                texto_publicaciones = "No hay publicaciones válidas."
        else:
            texto_publicaciones = "No hay publicaciones."

        self.query_one("#publicaciones", Static).update(texto_publicaciones)

    def on_button_pressed(self, event):
        if event.button.id == "volver":
            self.app.pop_screen()