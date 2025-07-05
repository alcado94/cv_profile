# Ajustes para la Versión Móvil del CV - Ubicación

## Resumen de Cambios

Se han realizado mejoras significativas en las plantillas del CV para optimizar la visualización de la ubicación y otros elementos en dispositivos móviles.

## Archivos Modificados

### 1. `templates/modern_cv.html`

**Problema identificado**: La plantilla modern_cv.html solo tenía una media query básica para dispositivos móviles (max-width: 900px) que no reorganizaba correctamente el layout para pantallas pequeñas.

**Mejoras implementadas**:

#### Media Query para Tablets (max-width: 900px)
- Cambio de `display: grid` a `display: flex` con `flex-direction: column`
- El sidebar ahora aparece en la parte superior, seguido del contenido principal
- La sección de perfil se reorganiza horizontalmente
- La información de contacto (incluyendo ubicación) se presenta en formato de pills con fondo gris claro
- Espaciado optimizado para mejor legibilidad

#### Media Query para Móviles (max-width: 600px)
- Layout completamente vertical y centrado
- Imagen de perfil más grande (100px)
- Información de contacto centrada con mayor tamaño de fuente
- Mejor espaciado entre elementos
- Sección de ubicación más prominente y legible

### 2. `templates/classic_cv.html`

**Mejoras implementadas**:
- Mejor centrado de la información de contacto en pantallas pequeñas
- Tamaño de fuente optimizado para la ubicación
- Mejor espaciado entre elementos de contacto

## Beneficios de los Cambios

1. **Mejor Experiencia Mobile**: La ubicación ahora es más fácil de leer en dispositivos móviles
2. **Layout Responsive**: El diseño se adapta fluidamente a diferentes tamaños de pantalla
3. **Información Prominente**: La ubicación (Galicia, España) es más visible y accesible
4. **Consistencia**: Ambas plantillas (modern y classic) tienen un comportamiento móvil coherente

## Detalles Técnicos

### Cambios CSS Principales

```css
/* Para tablets (900px) */
.cv-container {
    display: flex;
    flex-direction: column;
    grid-template-columns: none;
}

.contact-info {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
}

.contact-item {
    background-color: #f8f9fa;
    padding: 5px 10px;
    border-radius: 15px;
    border: 1px solid #e9ecef;
}

/* Para móviles (600px) */
.profile-section {
    flex-direction: column;
    text-align: center;
}

.contact-info {
    justify-content: center;
}
```

## Visualización de la Ubicación

La ubicación "Galicia, España" ahora se muestra:
- **En tablets**: Como un elemento destacado en la línea de información de contacto
- **En móviles**: Centrada y con mayor prominencia visual
- **Formato**: Pill/botón con fondo gris claro para mejor legibilidad

## Compatibilidad

Los cambios mantienen la compatibilidad con:
- Versión desktop (sin cambios)
- Versión de impresión (sin cambios)  
- Diferentes navegadores móviles
- Orientación portrait y landscape

## Estructura de Datos

La ubicación se extrae del archivo JSON en la estructura:
```json
"location": {
    "country": "España",
    "region": "Galicia",
    "municipality": "Ourense"
}
```

Y se renderiza como: `Galicia, España`