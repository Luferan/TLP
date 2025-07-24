from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="API de Libros",
    description="Una API para gestionar libros, usuarios y compras",
    version="1.0.0",
)

# Base de datos en memoria (simulada)
db = {
    "libros": [
        {"id": 1, "titulo": "El Principito", "autor": "Antoine de Saint-Exupéry", "precio": 15.99},
        {"id": 2, "titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "precio": 22.50},
    ],
    "usuarios": [],
    "carritos": {}
}

# Modelos Pydantic para validación de datos
class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    precio: float

class LibroCreate(BaseModel):
    titulo: str
    autor: str
    precio: float

class UsuarioCreate(BaseModel):
    nombre: str
    email: str

class ItemCarrito(BaseModel):
    libro_id: int
    cantidad: int = 1

# Operaciones con Libros
@app.get("/libros/", response_model=List[Libro], tags=["Libros"])
def listar_libros():
    """Obtener lista completa de libros disponibles"""
    return db["libros"]

@app.post("/libros/", response_model=Libro, status_code=201, tags=["Libros"])
def crear_libro(libro: LibroCreate):
    """Añadir un nuevo libro al catálogo"""
    nuevo_id = max([l["id"] for l in db["libros"]], default=0) + 1
    nuevo_libro = Libro(id=nuevo_id, **libro.dict())
    db["libros"].append(nuevo_libro.dict())
    return nuevo_libro

@app.delete("/libros/{libro_id}", tags=["Libros"])
def eliminar_libro(libro_id: int):
    """Eliminar un libro por su ID"""
    for i, libro in enumerate(db["libros"]):
        if libro["id"] == libro_id:
            db["libros"].pop(i)
            return {"mensaje": "Libro eliminado"}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

# Operaciones con Usuarios
@app.post("/usuarios/", status_code=201, tags=["Usuarios"])
def registrar_usuario(usuario: UsuarioCreate):
    """Registrar un nuevo usuario"""
    nuevo_id = len(db["usuarios"]) + 1
    nuevo_usuario = {
        "id": nuevo_id,
        "nombre": usuario.nombre,
        "email": usuario.email
    }
    db["usuarios"].append(nuevo_usuario)
    db["carritos"][nuevo_id] = []  # Crear carrito vacío
    return {"mensaje": "Usuario registrado", "id": nuevo_id}

# Operaciones con Carrito
@app.get("/carrito/{usuario_id}", tags=["Carrito"])
def ver_carrito(usuario_id: int):
    """Ver el contenido del carrito de un usuario"""
    if usuario_id not in db["carritos"]:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    carrito = []
    total = 0.0
    
    for item in db["carritos"][usuario_id]:
        libro = next((l for l in db["libros"] if l["id"] == item["libro_id"]), None)
        if libro:
            carrito.append({
                "libro": libro,
                "cantidad": item["cantidad"]
            })
            total += libro["precio"] * item["cantidad"]
    
    return {"items": carrito, "total": total}

@app.post("/carrito/{usuario_id}/agregar", tags=["Carrito"])
def agregar_al_carrito(usuario_id: int, item: ItemCarrito):
    """Añadir un libro al carrito de compras"""
    if usuario_id not in db["carritos"]:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not any(l["id"] == item.libro_id for l in db["libros"]):
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    db["carritos"][usuario_id].append(item.dict())
    return {"mensaje": "Libro añadido al carrito"}

@app.delete("/carrito/{usuario_id}/vaciar", tags=["Carrito"])
def vaciar_carrito(usuario_id: int):
    """Vaciar el carrito de compras"""
    if usuario_id not in db["carritos"]:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db["carritos"][usuario_id] = []
    return {"mensaje": "Carrito vaciado"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)