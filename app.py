# FILE: app.py
"""
Main Streamlit app for MiniMarket Manager
Three-file project:
 - app.py (this file)
 - inventory_manager.py
 - shifts_manager.py

No dataset required. Uses st.session_state to persist in-session.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from inventory_manager import InventoryManager
from shifts_manager import ShiftsManager
import plotly.express as px

st.set_page_config(page_title="MiniMarket Manager", layout="wide")

# Initialize managers
if "inventory_manager" not in st.session_state:
    st.session_state.inventory_manager = InventoryManager()

if "shifts_manager" not in st.session_state:
    st.session_state.shifts_manager = ShiftsManager()

inv_mgr: InventoryManager = st.session_state.inventory_manager
shf_mgr: ShiftsManager = st.session_state.shifts_manager

# --- Sidebar navigation ---
st.sidebar.title("MiniMarket Manager")
page = st.sidebar.radio("Navegación", ["Dashboard", "Inventario", "Turnos & Autoevaluación"])

# --- Dashboard ---
if page == "Dashboard":
    st.header("Panel de control — Indicadores logísticos clave")
    # KPIs
    total_products = inv_mgr.total_skus()
    total_units = inv_mgr.total_units()
    avg_stock = inv_mgr.average_stock()
    low_stock_pct = inv_mgr.low_stock_percentage()
    compliance_rate = shf_mgr.overall_compliance_rate()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("SKUs", f"{total_products}")
    kpi2.metric("Unidades en stock", f"{total_units}")
    kpi3.metric("Stock promedio por SKU", f"{avg_stock:.1f}")
    kpi4.metric("% Items bajo stock", f"{low_stock_pct:.1f}%")
    kpi5.metric("Cumplimiento (autoeval)", f"{compliance_rate:.1f}%")

    st.markdown("---")
    # Charts area
    col1, col2 = st.columns([2, 1])

    # Top products by stock
    with col1:
        st.subheader("Top productos por existencias")
        df_top = inv_mgr.df().sort_values(by="stock", ascending=False).head(10)
        if not df_top.empty:
            fig_bar = px.bar(df_top, x="product_name", y="stock", labels={"product_name":"Producto","stock":"Unidades"}, title="Top 10 productos en stock")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Aún no hay productos. Ve a Inventario para añadir algunos.")

    with col2:
        st.subheader("Composición de estado de stock")
        df = inv_mgr.df()
        if not df.empty:
            df_status = df.assign(status=df["stock"].apply(lambda x: "Bajo" if x <= df['reorder_level'].fillna(0).mean() else "Normal"))
            fig_pie = px.pie(df_status, names="status", title="% Bajo vs Normal")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sin datos de inventario para mostrar pie chart.")

    st.markdown("---")
    st.subheader("Cumplimiento de tareas por día (autoevaluaciones)")
    df_shifts = shf_mgr.df()
    if not df_shifts.empty:
        df_shifts['date'] = pd.to_datetime(df_shifts['clock_in']).dt.date
        daily = df_shifts.groupby('date')[['cleaning','orderly','restock']].mean().reset_index()
        daily = daily.melt(id_vars='date', var_name='task', value_name='compliance')
        fig_line = px.line(daily, x='date', y='compliance', color='task', markers=True, labels={'compliance':'% Cumplimiento (0-1)'}, title='Tendencia diaria de cumplimiento')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info('Aún no hay registros de turnos. Ve a Turnos & Autoevaluación para registrar.')

# --- Inventory management ---
elif page == "Inventario":
    st.header("Gestor de Inventario")
    st.markdown("Panel para añadir, editar y eliminar productos. También actualizar stock rápidamente.")

    with st.expander("Añadir producto nuevo"):
        with st.form("add_product_form"):
            name = st.text_input("Nombre del producto")
            sku = st.text_input("SKU (opcional)")
            category = st.text_input("Categoría (opcional)")
            stock = st.number_input("Stock inicial", min_value=0, value=0)
            reorder = st.number_input("Nivel de reorden (reorder level)", min_value=0, value=5)
            price = st.number_input("Precio unitario (opcional)", min_value=0.0, value=0.0, format="%.2f")
            add_btn = st.form_submit_button("Añadir producto")
        if add_btn:
            if name.strip() == "":
                st.warning("El nombre no puede estar vacío.")
            else:
                inv_mgr.add_product(name, sku or None, category or None, int(stock), int(reorder), float(price))
                st.success(f"Producto '{name}' añadido.")

    st.markdown("---")
    st.subheader("Inventario actual")
    df = inv_mgr.df()
    if df.empty:
        st.info("No hay productos. Añade uno arriba.")
    else:
        st.dataframe(df)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Editar producto")
        prod_to_edit = st.selectbox("Seleccionar producto", options=df['product_id'].tolist(), format_func=lambda x: inv_mgr.get_by_id(x)['product_name'] if inv_mgr.get_by_id(x) else str(x))
        if prod_to_edit:
            p = inv_mgr.get_by_id(prod_to_edit)
            with st.form("edit_form"):
                new_name = st.text_input("Nombre", value=p['product_name'])
                new_sku = st.text_input("SKU", value=p.get('sku','') or '')
                new_cat = st.text_input("Categoría", value=p.get('category','') or '')
                new_stock = st.number_input("Stock", min_value=0, value=int(p['stock']))
                new_reorder = st.number_input("Reorder level", min_value=0, value=int(p.get('reorder_level',5)))
                new_price = st.number_input("Precio unitario", min_value=0.0, value=float(p.get('price',0.0)), format="%.2f")
                save = st.form_submit_button("Guardar cambios")
            if save:
                inv_mgr.edit_product(prod_to_edit, new_name, new_sku or None, new_cat or None, int(new_stock), int(new_reorder), float(new_price))
                st.success("Producto actualizado.")

    with col_b:
        st.subheader("Eliminar / Ajustar stock")
        prod_to_del = st.selectbox("Seleccionar producto para acción", options=df['product_id'].tolist(), format_func=lambda x: inv_mgr.get_by_id(x)['product_name'] if inv_mgr.get_by_id(x) else str(x))
        if prod_to_del:
            p = inv_mgr.get_by_id(prod_to_del)
            st.write(p)
            if st.button("Eliminar producto"):
                inv_mgr.delete_product(prod_to_del)
                st.success("Producto eliminado.")

            st.markdown("**Ajuste rápido de stock**")
            with st.form("adj_stock"):
                adj = st.number_input("Ajuste (positivo o negativo)", value=0, step=1)
                adj_submit = st.form_submit_button("Aplicar ajuste")
            if adj_submit:
                inv_mgr.update_stock(prod_to_del, int(adj))
                st.success("Stock ajustado.")

# --- Shifts & self-eval ---
elif page == "Turnos & Autoevaluación":
    st.header("Registro de turnos y autoevaluación")
    st.markdown("Trabajadores registran ingreso/salida y marcan cumplimiento de actividades: Limpieza, Ordenamiento/llenado de anaqueles, Cuadro de caja chica.")

    with st.form("shift_form"):
        worker = st.text_input("Nombre del trabajador")
        clock_in = st.time_input("Hora de ingreso", value=datetime.now().time())
        clock_out = st.time_input("Hora de salida", value=(datetime.now().time()))
        cleaning = st.checkbox("Limpieza cumplida")
        orderly = st.checkbox("Ordenamiento / llenado anaqueles cumplido")
        petty = st.checkbox("Cuadro de caja chica cumplido")
        submit_shift = st.form_submit_button("Registrar turno")
    if submit_shift:
        if worker.strip() == "":
            st.warning("Ingrese el nombre del trabajador.")
        else:
            # Compose full datetime strings using today's date
            today = datetime.now().date()
            dt_in = datetime.combine(today, clock_in)
            dt_out = datetime.combine(today, clock_out)
            shf_mgr.add_shift(worker.strip(), dt_in.isoformat(), dt_out.isoformat(), cleaning, orderly, petty)
            st.success("Turno registrado.")

    st.markdown("---")
    st.subheader("Historial de turnos")
    df_sh = shf_mgr.df()
    if df_sh.empty:
        st.info("No hay registros de turnos.")
    else:
        st.dataframe(df_sh)

    st.markdown("---")
    st.subheader("Acciones de supervisión")
    # Quick compliance summary
    compliance = shf_mgr.compliance_summary()
    st.table(pd.DataFrame([compliance]))
