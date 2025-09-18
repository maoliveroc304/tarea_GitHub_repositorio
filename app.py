# FILE: app.py
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


# End of app.py