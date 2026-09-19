import streamlit as st
import json
import base64
from datetime import datetime, time

# Configuración de la página
st.set_page_config(
    page_title="SIU - Control de Visitas",
    page_icon="🎓",
    layout="wide"
)

# Inicializar almacenamiento temporal (Estado de la Sesión)
if "visitas" not in st.session_state:
    st.session_state.visitas = [
        {
            "id": "1",
            "nombreColegio": "Colegio Félix Olivares Contreras",
            "ubicacion": "Calle 4ta Este",
            "distrito": "David",
            "cantidadEstudiantes": 1200,
            "dia": "Lunes",
            "hora": "09:30",
            "nombrePersona": "Carlos Mendoza",
            "observacion": "Supervisión de equipos informáticos.",
            "fotos": []
        }
    ]

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# Función auxiliar para convertir imágenes a Base64
def imagen_a_base64(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_str = base64.b64encode(bytes_data).decode("utf-8")
    return f"data:{uploaded_file.type};base64,{base64_str}"

# --- ENCABEZADO ---
st.title("🎓 SIU - Control de Visitas a Colegios")
st.caption("Distrito de David, Chiriquí | Sistema de Registro Web CRUD")
st.divider()

# --- ESTRUCTURA EN COLUMNAS ---
col_form, col_tabla = st.columns([5, 7], gap="large")

# ==========================================
# COLUMNA IZQUIERDA: FORMULARIO DE REGISTRO / EDICIÓN
# ==========================================
with col_form:
    if st.session_state.edit_id:
        st.subheader("✏️ Editar Visita Registrada")
        registro_actual = next((v for v in st.session_state.visitas if v["id"] == st.session_state.edit_id), None)
    else:
        st.subheader("📝 Registro de Visita")
        registro_actual = None

    with st.form("visit_form", clear_on_submit=False):
        # Campos de texto simples
        nombreColegio = st.text_input(
            "Nombre del Colegio *", 
            value=registro_actual["nombreColegio"] if registro_actual else ""
        )
        
        c1, c2 = st.columns(2)
        with c1:
            ubicacion = st.text_input(
                "Ubicación *", 
                value=registro_actual["ubicacion"] if registro_actual else ""
            )
        with c2:
            opciones_distrito = ["David", "Dolega", "Bugaba", "Boquete", "Barú", "Otro"]
            idx_dist = opciones_distrito.index(registro_actual["distrito"]) if registro_actual and registro_actual["distrito"] in opciones_distrito else 0
            distrito = st.selectbox("Distrito *", opciones_distrito, index=idx_dist)

        c3, c4 = st.columns(2)
        with c3:
            cantidadEstudiantes = st.number_input(
                "Estudiantes *", 
                min_value=1, 
                step=1, 
                value=int(registro_actual["cantidadEstudiantes"]) if registro_actual else 100
            )
        with c4:
            opciones_dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
            idx_dia = opciones_dia.index(registro_actual["dia"]) if registro_actual and registro_actual["dia"] in opciones_dia else 0
            dia = st.selectbox("Día de Visita *", opciones_dia, index=idx_dia)

        c5, c6 = st.columns(2)
        with c5:
            # Formato 24 Horas
            if registro_actual:
                h_parts = list(map(int, registro_actual["hora"].split(":")))
                val_hora = time(h_parts[0], h_parts[1])
            else:
                val_hora = time(8, 0)
            hora_obj = st.time_input("Hora (24 Horas) *", value=val_hora)
            hora_str = hora_obj.strftime("%H:%M")
        with c6:
            nombrePersona = st.text_input(
                "Nombre Persona *", 
                value=registro_actual["nombrePersona"] if registro_actual else ""
            )

        observacion = st.text_area(
            "Observación", 
            value=registro_actual["observacion"] if registro_actual else ""
        )

        # Carga de fotos con validación estricta (Mínimo 2, Máximo 4)
        st.markdown("**Fotografías (Mínimo 2, Máximo 4) ***")
        fotos_subidas = st.file_uploader(
            "Seleccione entre 2 y 4 imágenes", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )

        btn_label = "💾 Actualizar Registro" if st.session_state.edit_id else "💾 Guardar Registro"
        submitted = st.form_submit_button(btn_label, use_container_width=True)

        if submitted:
            # Validaciones de campos y fotos
            if not nombreColegio or not ubicacion or not nombrePersona:
                st.error("Por favor, complete todos los campos obligatorios (*).")
            elif len(fotos_subidas) < 2 or len(fotos_subidas) > 4:
                st.error(f"Error: Debe seleccionar entre 2 y 4 fotografías (Ha seleccionado {len(fotos_subidas)}).")
            else:
                # Convertir fotos a Base64 para el JSON
                fotos_base64 = [imagen_a_base64(f) for f in fotos_subidas]

                nuevo_registro = {
                    "id": st.session_state.edit_id if st.session_state.edit_id else str(datetime.now().timestamp()),
                    "nombreColegio": nombreColegio,
                    "ubicacion": ubicacion,
                    "distrito": distrito,
                    "cantidadEstudiantes": cantidadEstudiantes,
                    "dia": dia,
                    "hora": hora_str,
                    "nombrePersona": nombrePersona,
                    "observacion": observacion,
                    "fotos": fotos_base64
                }

                if st.session_state.edit_id:
                    # Actualizar (Update)
                    st.session_state.visitas = [
                        nuevo_registro if v["id"] == st.session_state.edit_id else v 
                        for v in st.session_state.visitas
                    ]
                    st.session_state.edit_id = None
                    st.success("¡Registro actualizado exitosamente!")
                else:
                    # Crear (Create)
                    st.session_state.visitas.append(nuevo_registro)
                    st.success("¡Registro guardado exitosamente!")
                st.rerun()

    if st.session_state.edit_id:
        if st.button("Cancelar Edición"):
            st.session_state.edit_id = None
            st.rerun()

# ==========================================
# COLUMNA DERECHA: TABLA CRUD Y EXPORTACIÓN JSON
# ==========================================
with col_tabla:
    st.subheader("📋 Visitas Registradas")

    if not st.session_state.visitas:
        st.info("No hay visitas registradas en el sistema.")
    else:
        for idx, item in enumerate(st.session_state.visitas):
            with st.expander(f"🏫 **{item['nombreColegio']}** - {item['dia']} ({item['hora']} hrs)", expanded=False):
                st.write(f"**Ubicación / Distrito:** {item['ubicacion']}, {item['distrito']}")
                st.write(f"**Estudiantes:** {item['cantidadEstudiantes']} | **Atendió:** {item['nombrePersona']}")
                st.write(f"**Observación:** {item['observacion']}")
                st.write(f"**Fotos adjuntas:** {len(item['fotos'])} imágenes")

                # Botones de Acción (Editar / Eliminar)
                c_edit, c_del = st.columns(2)
                with c_edit:
                    if st.button("✏️ Editar", key=f"edit_{item['id']}"):
                        st.session_state.edit_id = item["id"]
                        st.rerun()
                with c_del:
                    if st.button("🗑️ Eliminar", key=f"del_{item['id']}"):
                        st.session_state.visitas = [v for v in st.session_state.visitas if v["id"] != item["id"]]
                        if st.session_state.edit_id == item["id"]:
                            st.session_state.edit_id = None
                        st.success("Registro eliminado.")
                        st.rerun()

    st.divider()

    # --- SIMULACIÓN DE ENVÍO Y EXPORTACIÓN JSON ---
    st.subheader("✉️ Remitir Archivo JSON al Supervisor")
    payload_json = {
        "remitente": "personal_siu@utp.ac.pa",
        "destinatario": "docente_supervisor@utp.ac.pa",
        "fecha_generacion": datetime.now().isoformat(),
        "total_registros": len(st.session_state.visitas),
        "visitas": st.session_state.visitas
    }

    json_bytes = json.dumps(payload_json, indent=4, ensure_ascii=False).encode('utf-8')

    st.download_button(
        label="📥 Descargar/Generar JSON de Envío",
        data=json_bytes,
        file_name="reporte_visitas_siu.json",
        mime="application/json",
        use_container_width=True
    )