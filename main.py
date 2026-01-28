import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="simplayce | Advanced Simulator",
    page_icon="🏢",
    layout="wide"
)

# --- 2. CUSTOM CSS (DARK MODE OPTIMIZED) ---
# Das hier fixet die "weißen Kästen". Wir erzwingen dunkle Hintergründe für die Boxen.
st.markdown("""
<style>
    /* KPI Boxen Styling für Dark Mode */
    div.stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #464b5c;
    }
    /* Schriftfarbe in Metrics erzwingen (falls Streamlit zickt) */
    div.stMetric > div { color: white !important; }
    
    /* Etwas Abstand für die Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: KONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Simulations-Parameter")
    
    st.subheader("1. Struktur")
    # Department Editor
    st.info("👥 **Abteilungs-Matrix**")
    
    # Standard-Daten (Mockup)
    default_data = pd.DataFrame([
        {"Abteilung": "Sales", "MA": 40, "Remote_Faktor": 0.8},
        {"Abteilung": "IT / Dev", "MA": 60, "Remote_Faktor": 0.9},
        {"Abteilung": "HR / Admin", "MA": 20, "Remote_Faktor": 0.5},
    ])
    
    # Der Editor
    edited_df = st.data_editor(
        default_data, 
        num_rows="dynamic", 
        hide_index=True,
        column_config={
            "Remote_Faktor": st.column_config.NumberColumn(
                "Remote (0-1)", min_value=0.0, max_value=1.0, step=0.1, format="%.1f"
            )
        }
    )
    
    total_employees = edited_df["MA"].sum()
    st.write(f"**Total FTE:** {total_employees}")

    st.subheader("2. Policy & AI")
    sharing_ratio = st.slider("Desk Sharing Quote", 0.5, 1.2, 0.8, help="0.8 = 8 Tische für 10 Leute")
    ai_impact = st.slider("AI Efficiency Impact", 0, 30, 10, format="%d%%", help="Flächenersparnis durch Automatisierung")
    
    st.markdown("---")
    st.caption("Advanced Simulation v1.1 (Dark Mode Fix)")

# --- 4. CALCULATION ENGINE ---
results = []
total_required_desks = 0
total_baseline_desks = total_employees

for index, row in edited_df.iterrows():
    # Logik: MA * (Sharing_Impact) * (1 - AI) - vereinfacht
    dept_remote = row["Remote_Faktor"]
    
    # Basisbedarf mit Sharing
    dept_need = row["MA"] * sharing_ratio 
    
    # Wenn Remote hoch ist (>0.5), greift Sharing noch besser
    if dept_remote > 0.5:
        dept_need = dept_need * 0.9 
    
    # AI Impact zieht pauschal ab
    dept_need = dept_need * (1 - (ai_impact/100))
    
    results.append({
        "Abteilung": row["Abteilung"], 
        "Bedarf": int(dept_need),
        "Einsparung": int(row["MA"] - dept_need)
    })
    total_required_desks += int(dept_need)

df_results = pd.DataFrame(results)

# Financials
sqm_per_desk = 12
rent = 28.50
baseline_cost = total_baseline_desks * sqm_per_desk * rent * 12
new_cost = total_required_desks * sqm_per_desk * rent * 12
savings = baseline_cost - new_cost

# --- 5. MAIN DASHBOARD ---
st.title("🏢 simplayce | Interactive Simulation")
st.markdown(f"Status: **{total_employees} Mitarbeiter** | AI-Impact: **{ai_impact}%**")

# KPI ROW
c1, c2, c3, c4 = st.columns(4)
c1.metric("Arbeitsplätze (Neu)", f"{total_required_desks}", delta=f"{total_required_desks - total_baseline_desks}", delta_color="inverse")
c2.metric("Fläche (Neu)", f"{total_required_desks * sqm_per_desk:,.0f} m²", delta=f"{(total_required_desks - total_baseline_desks) * sqm_per_desk:,.0f} m²", delta_color="inverse")
c3.metric("Mietkosten (p.a.)", f"{new_cost:,.0f} €", delta=f"- {savings:,.0f} €", delta_color="normal")
c4.metric("CO₂ Reduktion", f"{int(savings/1000 * 0.4)} t", delta="ESG Ziel", delta_color="normal")

st.markdown("---")

# VISUALISIERUNG
tab1, tab2 = st.tabs(["🗺️ Space Heatmap (Simulation)", "📊 Peak Analysis"])

with tab1:
    st.subheader("Dynamische Flächenbelegung")
    st.markdown("Visualisierung der eingesparten Flächen basierend auf Department-Daten.")
    
    c_map, c_legend = st.columns([3, 1])
    
    with c_map:
        # HEATMAP GENERATOR
        grid_size = int(np.ceil(np.sqrt(total_employees)))
        grid_data = []
        
        for i in range(grid_size * grid_size):
            x, y = i % grid_size, i // grid_size
            
            # Status Logik
            if i < total_required_desks:
                status = "Belegt (Aktiv)"
                val = 2
            elif i < total_baseline_desks:
                status = "Eingespart (Remote/AI)"
                val = 1
            else:
                status = "Reserve" 
                val = 0
                
            if i < total_employees * 1.1: 
                grid_data.append({"x": x, "y": y, "Status": status, "val": val})

        df_grid = pd.DataFrame(grid_data)
        
        fig_map = px.scatter(
            df_grid, x="x", y="y", color="Status",
            color_discrete_map={"Belegt (Aktiv)": "#ef553b", "Eingespart (Remote/AI)": "#00cc96", "Reserve": "#262730"},
            symbol_sequence=["square"], height=500
        )
        fig_map.update_traces(marker=dict(size=18, line=dict(width=0))) # Randlos für cleaneren Look
        
        # DARK MODE FIX für Plotly
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", # Transparent
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent
            font=dict(color="white"),      # Weiße Schrift
            xaxis=dict(showgrid=False, visible=False), 
            yaxis=dict(showgrid=False, visible=False, scaleanchor="x"),
            margin=dict(t=10,l=10,r=10,b=10),
            legend=dict(orientation="h", y=1.05, font=dict(color="white"))
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with c_legend:
        # Custom Legende in einer Box
        st.info("""
        **Legende:**
        
        🔴 **Rot:** Benötigte Tische
        
        🟢 **Grün:** Durch New Work & AI eingesparte Fläche (= Cash Savings)
        
        ⚫ **Dunkel:** Reserve / Nicht genutzt
        """)

with tab2:
    st.subheader("Auslastung nach Abteilungen")
    
    fig_bar = px.bar(
        df_results, x="Abteilung", y=["Bedarf", "Einsparung"], 
        title="Optimierungspotenzial pro Department",
        color_discrete_map={"Bedarf": "#3498db", "Einsparung": "#95a5a6"}
    )
    
    # DARK MODE FIX für Bar Chart
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(font=dict(color="white"))
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

# 6. AI INSIGHT BOX
with st.expander("🤖 AI Readiness Analyse anzeigen"):
    st.markdown(f"""
    Basierend auf einem AI-Efficiency Impact von **{ai_impact}%** prognostiziert das Modell eine Reduktion von 
    administrativen Tätigkeiten. 
    
    Dies ermöglicht eine Umwandlung von **{int(total_required_desks * 0.1)} Standard-Tischen** in "Collaboration Zones".
    """)