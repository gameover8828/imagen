import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os
import math
import random
import urllib.request

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Generador de Ofertas Pro",
    page_icon="🛒",
    layout="wide",
)

# --- INICIALIZAR ESTADO DE SESIÓN ---
keys_texto = ["prod_name", "prod_price", "prod_link", "prod_orig_price", "desc_txt"]
for key in keys_texto:
    if key not in st.session_state:
        st.session_state[key] = ""

if "reset_uploader" not in st.session_state:
    st.session_state.reset_uploader = 0

def limpiar_datos():
    for k in keys_texto:
        st.session_state[k] = ""
    st.session_state.reset_uploader += 1 

# --- SISTEMA ULTRA ROBUSTO DE FUENTES ---
@st.cache_resource
def descargar_fuente():
    """Descarga la fuente y verifica que no esté corrupta o vacía."""
    font_name = "Montserrat-Bold.ttf"
    
    # Si no existe o pesa menos de 10KB (archivo corrupto), la descargamos
    if not os.path.exists(font_name) or os.path.getsize(font_name) < 10000:
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response, open(font_name, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print(f"No se pudo descargar la fuente: {e}")
    
    return font_name

def obtener_fuente(size):
    font_name = descargar_fuente()
    
    # Lista de fuentes de respaldo por Sistema Operativo
    opciones_fuente = [
        font_name, 
        "arialbd.ttf",        # Windows
        "Arial Bold.ttf",     # Mac
        "DejaVuSans-Bold.ttf",# Linux
        "FreeSansBold.ttf"    # Linux alternativa
    ]
    
    for op in opciones_fuente:
        try:
            return ImageFont.truetype(op, size)
        except:
            continue
            
    # Si TODO falla, intentamos usar el default escalable (Requiere Pillow >= 10.1.0)
    try:
        return ImageFont.load_default(size=size)
    except:
        return ImageFont.load_default()

# --- FUNCIONES DE DIBUJO AVANZADO ---
def dibujar_texto_neon(draw, img_base, xy, texto, fuente, color_texto, color_glow, anchor="mm", grosor_glow=8):
    """Crea un efecto de resplandor (glow) detrás del texto."""
    x, y = xy
    capa_glow = Image.new("RGBA", img_base.size, (0,0,0,0))
    d_glow = ImageDraw.Draw(capa_glow)
    d_glow.text((x, y+5), texto, fill=color_glow, font=fuente, anchor=anchor, stroke_width=grosor_glow, stroke_fill=color_glow)
    capa_glow = capa_glow.filter(ImageFilter.GaussianBlur(10))
    img_base.paste(capa_glow, (0,0), capa_glow)
    
    draw.text((x, y), texto, fill=color_texto, font=fuente, anchor=anchor, stroke_width=3, stroke_fill=(255,255,255,100))

def crear_liston_roto(ancho, alto, texto, fuente):
    """Crea un listón rojo rasgado con borde amarillo."""
    img_liston = Image.new("RGBA", (ancho + 100, alto + 100), (0,0,0,0))
    d = ImageDraw.Draw(img_liston)
    x, y, w, h = 50, 50, ancho, alto
    
    # Borde Amarillo (Sombra trasera rasgada)
    puntos_sombra = [
        (x-20, y-10), (x+w//2, y-30), (x+w+20, y-10),
        (x+w-10, y+h//2), (x+w+30, y+h+20),
        (x+w//2, y+h+40), (x-30, y+h+10), (x+10, y+h//2)
    ]
    d.polygon(puntos_sombra, fill=(255, 215, 0, 255)) 
    
    # Fondo Rojo Principal
    puntos_rojos = [
        (x, y), (x+w//2, y-15), (x+w, y),
        (x+w-20, y+h//2), (x+w+10, y+h),
        (x+w//2, y+h+15), (x-10, y+h), (x+20, y+h//2)
    ]
    d.polygon(puntos_rojos, fill=(230, 20, 0, 255)) 
    
    # Texto centrado gigante
    d.text((x + w//2, y + h//2), texto, fill=(255, 255, 255, 255), font=fuente, anchor="mm", stroke_width=6, stroke_fill=(150, 0, 0, 255))
    
    return img_liston

def draw_neon_scalloped_badge(img_base, cx, cy, r_outer, r_inner, points):
    """Dibuja un sello estrellado con efecto neón cyan y fondo oscuro."""
    # Capa para el resplandor
    glow_layer = Image.new("RGBA", img_base.size, (0,0,0,0))
    d_glow = ImageDraw.Draw(glow_layer)
    
    poly = []
    for i in range(points * 2):
        angle = i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        poly.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    
    # Dibujar resplandor exterior cyan
    d_glow.polygon(poly, fill=(0, 255, 255, 80))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
    img_base.paste(glow_layer, (0,0), glow_layer)
    
    # Dibujar polígono base (sello principal) en la imagen
    draw = ImageDraw.Draw(img_base)
    draw.polygon(poly, fill=(10, 40, 80, 255)) # Azul muy oscuro (fondo del sello)
    poly.append(poly[0]) # Cerrar poligono para la linea
    draw.line(poly, fill=(0, 255, 255, 255), width=8, joint="curve") # Borde Cyan Neón
    
    # Línea interna (círculo interior punteado o continuo)
    draw.ellipse([(cx - r_inner + 15, cy - r_inner + 15), (cx + r_inner - 15, cy + r_inner - 15)], outline=(0, 255, 255, 180), width=3)
    
    return draw

# --- INTERFAZ PRINCIPAL ---
st.title("🛒 Generador de Ofertas Pro (Estilo Neón)")

st.header("1. Datos Generales del Producto")
col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
with col1:
    producto = st.text_input("Nombre del Producto", placeholder="Ej. Audífonos Gamer", key="prod_name")
with col2:
    precio = st.text_input("Precio de Oferta", placeholder="Ej. 168.98", key="prod_price")
with col3:
    link_ml = st.text_input("Link de Compra", placeholder="https://meli.la/...", key="prod_link")
with col4:
    st.write("") 
    st.button("🧹 Limpiar Todo", on_click=limpiar_datos, type="primary", use_container_width=True)

st.divider()

tab1, tab2 = st.tabs(["🖼️ Creador de Imagen Premium", "🎵 Descripción para TikTok"])

with tab1:
    col_izq, col_der = st.columns([1, 2])
    
    with col_izq:
        st.markdown("### 🎛️ Elementos de Imagen")
        imagen_subida = st.file_uploader("Sube la foto de tu producto", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.reset_uploader}")
        precio_original_txt = st.text_input("Precio Original Tachado", placeholder="Ej. 259.98", key="prod_orig_price")
        porcentaje_desc_txt = st.text_input("Texto del Descuento", value="¡34% OFF!", key="desc_txt")
        
        st.markdown("### 🎚️ Ajuste de Tamaños (Letras)")
        tamano_liston = st.slider("Tamaño: Texto del Descuento", min_value=50, max_value=250, value=170)
        tamano_tachado = st.slider("Tamaño: Precio Tachado", min_value=50, max_value=150, value=100)
        tamano_precio = st.slider("Tamaño: Precio Oferta", min_value=100, max_value=300, value=220)
        tamano_sello = st.slider("Tamaño: Letra MÁS VENDIDO", min_value=30, max_value=100, value=60)

    with col_der:
        if imagen_subida and precio and precio_original_txt:
            ancho, alto = 1080, 1920 
            
            # 1. FONDO AZUL DEGRADADO
            banner_base = Image.new("RGBA", (ancho, alto), (30, 100, 255, 255))
            draw = ImageDraw.Draw(banner_base)
            
            # Resplandor cyan en el centro
            glow_bg = Image.new("RGBA", (ancho, alto), (0,0,0,0))
            d_glow = ImageDraw.Draw(glow_bg)
            d_glow.ellipse([(-200, 300), (1280, 1400)], fill=(0, 200, 255, 120))
            glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(150))
            banner_base.paste(glow_bg, (0,0), glow_bg)
            
            # Confeti
            colores_confeti = [(255, 215, 0), (200, 200, 200), (0, 255, 255), (255, 100, 100)]
            for _ in range(70):
                x = random.randint(20, ancho-20)
                y = random.randint(20, alto-20)
                tam_x = random.randint(15, 40)
                tam_y = random.randint(10, 20)
                color = random.choice(colores_confeti)
                
                img_confeti = Image.new("RGBA", (tam_x, tam_y), color)
                img_confeti = img_confeti.rotate(random.randint(0, 360), expand=True)
                banner_base.paste(img_confeti, (x, y), img_confeti)

            # 2. CARGAR FUENTES ESCALABLES (Sistema Protegido)
            font_titulo = obtener_fuente(100)
            f_liston = obtener_fuente(tamano_liston)
            f_tachado = obtener_fuente(tamano_tachado)
            f_precio_final = obtener_fuente(tamano_precio)
            f_sello = obtener_fuente(tamano_sello)
            f_sello_mini = obtener_fuente(max(20, tamano_sello - 20))

            # 3. TÍTULO "OFERTA RELÁMPAGO"
            texto_oferta = "⚡ OFERTA RELÁMPAGO ⚡"
            dibujar_texto_neon(draw, banner_base, (ancho//2, 160), texto_oferta, font_titulo, (255, 255, 255, 255), (0, 200, 255, 255))

            # 4. IMAGEN DEL PRODUCTO CON SOMBRA
            img_prod = Image.open(imagen_subida).convert("RGBA")
            w_orig, h_orig = img_prod.size
            nuevo_alto = 900 
            nuevo_ancho = int((nuevo_alto / h_orig) * w_orig)
            if nuevo_ancho > ancho * 0.90:
                nuevo_ancho = int(ancho * 0.90)
                nuevo_alto = int((nuevo_ancho / w_orig) * h_orig)
                
            img_prod = img_prod.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            pos_prod_x = (ancho - nuevo_ancho) // 2
            pos_prod_y = 350 
            
            sombra_prod = Image.new("RGBA", (nuevo_ancho, nuevo_alto), (0,0,0,0))
            sombra_draw = ImageDraw.Draw(sombra_prod)
            sombra_draw.rectangle([(50, 50), (nuevo_ancho-50, nuevo_alto-50)], fill=(0,0,0,180))
            sombra_prod = sombra_prod.filter(ImageFilter.GaussianBlur(40))
            banner_base.paste(sombra_prod, (pos_prod_x, pos_prod_y+20), sombra_prod)
            banner_base.paste(img_prod, (pos_prod_x, pos_prod_y), img_prod)

            # 5. SELLO "MÁS VENDIDO" (Estilo Estrellado Neón)
            pos_sello_x, pos_sello_y = 850, 380
            draw = draw_neon_scalloped_badge(banner_base, pos_sello_x, pos_sello_y, r_outer=180, r_inner=150, points=16)
            
            # Texto dentro del sello
            draw.text((pos_sello_x, pos_sello_y - (tamano_sello//2) + 10), "MÁS", fill=(255, 255, 255), font=f_sello, anchor="mm")
            draw.text((pos_sello_x, pos_sello_y + (tamano_sello//2) + 10), "VENDIDO", fill=(0, 255, 255), font=f_sello_mini, anchor="mm")

            # 6. LISTÓN "34% OFF" ROTO E INCLINADO
            liston = crear_liston_roto(950, 250, porcentaje_desc_txt, f_liston)
            liston_rotado = liston.rotate(10, expand=True) 
            pos_liston_x = (ancho - liston_rotado.width) // 2
            pos_liston_y = 900 
            
            sombra_liston = Image.new("RGBA", liston_rotado.size, (0,0,0,0))
            sombra_liston.paste(liston_rotado, (0,0), liston_rotado)
            sombra_liston = sombra_liston.filter(ImageFilter.GaussianBlur(15))
            
            banner_base.paste(sombra_liston, (pos_liston_x+10, pos_liston_y+20), liston_rotado)
            banner_base.paste(liston_rotado, (pos_liston_x, pos_liston_y), liston_rotado)

            # 7. PRECIOS INFERIORES
            precio_orig_y = 1550
            precio_final_y = 1750
            
            # Precio Tachado
            texto_original_str = f"${precio_original_txt}"
            w_tachado = draw.textlength(texto_original_str, font=f_tachado)
            draw.text((ancho//2 + 5, precio_orig_y + 5), texto_original_str, fill=(0, 0, 0, 150), font=f_tachado, anchor="mm") 
            draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(255, 255, 255, 255), font=f_tachado, anchor="mm")
            
            # Grosor dinámico de la línea roja
            grosor_tachado = max(6, tamano_tachado // 10)
            draw.line([(ancho//2 - w_tachado//2 - 20, precio_orig_y), (ancho//2 + w_tachado//2 + 20, precio_orig_y)], fill=(255, 50, 50), width=grosor_tachado)
            
            # Precio Oferta (Verde Neón Gigante)
            texto_oferta_str = f"${precio} MXN"
            dibujar_texto_neon(draw, banner_base, (ancho//2, precio_final_y), texto_oferta_str, f_precio_final, (100, 255, 100), (0, 150, 0), grosor_glow=15)

            buffered = BytesIO()
            banner_base.save(buffered, format="PNG")
            
            st.image(buffered.getvalue(), caption="Diseño Premium Generado", use_container_width=True)
            st.download_button(label="📥 Descargar Imagen", data=buffered.getvalue(), file_name=f"banner_pro_{producto.replace(' ', '_')}.png", mime="image/png", use_container_width=True)
        else:
            st.info("👆 Sube la imagen y asegúrate de llenar Precio y Precio Original en la barra izquierda para generar el diseño.")

with tab2:
    if producto and precio and link_ml:
        st.subheader("📱 Copia esta descripción para tu video de TikTok")
        hashtag_producto = f"#{producto.replace(' ', '').lower()}"
        texto_tiktok = f"""🔥 ¡OFERTA RELÁMPAGO! 🔥\n\n¡No dejes pasar esta oportunidad! El {producto} que buscabas.\n\n💰 Llevátelo por solo $ {precio} MXN. 😱\n\n👉 Cómpralo de forma segura aquí: \n{link_ml}\n\n#ofertas #descuentos #promocion {hashtag_producto} #comprasonline"""
        st.code(texto_tiktok, language="text")
    else:
        st.info("Llena el Nombre del Producto, Precio y Link en la parte superior para generar la descripción.")
