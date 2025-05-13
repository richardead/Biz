import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🖍️ Rysowanie funkcji i normalizacja")

st.markdown("""
Wprowadź punkty funkcji ręcznie (przynajmniej 2 punkty, bez powtórzeń w osi X).<br>
Aplikacja pobierze z niej 80 próbek, znormalizuje do żądanej sumy, i pokaże wynik.
""", unsafe_allow_html=True)

# Suwaki do ustawienia zakresu
col1, col2 = st.columns(2)
with col1:
    y_min = st.slider("Minimalna wartość funkcji", -100.0, 100.0, 0.0)
with col2:
    y_max = st.slider("Maksymalna wartość funkcji", -100.0, 100.0, 1.0)

# Edytowalna tabela punktów
st.subheader("🔹 Wprowadź punkty funkcji")
default_points = {
    "x": [0.0, 0.5, 1.0],
    "y": [0.0, 0.8, 0.0]
}
points_df = st.data_editor(default_points, num_rows="dynamic", use_container_width=True)

if len(points_df["x"]) < 2:
    st.warning("Dodaj co najmniej dwa punkty.")
    st.stop()

# Przetwarzanie danych
x = np.array(points_df["x"])
y = np.array(points_df["y"])
sort_idx = np.argsort(x)
x = x[sort_idx]
y = y[sort_idx]

# Próbkowanie
x_sample = np.linspace(np.min(x), np.max(x), 80)
y_sample = np.interp(x_sample, x, y)

# Normalizacja
sum_before = np.sum(y_sample)
desired_sum = st.number_input("Pożądana suma próbek", value=float(sum_before))
offset = (desired_sum - sum_before) / 80
y_normalized = y_sample + offset

# Wykres
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(x, y, 'bo-', label="Oryginalna funkcja")
ax.plot(x_sample, y_normalized, 'g-', label="Znormalizowane próbki (80)")
ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
ax.legend()
ax.set_title("Porównanie funkcji i próbek")
ax.set_ylim(y_min - 1, y_max + 1)
st.pyplot(fig)

# Wyniki
st.write(f"🔸 Suma przed: `{sum_before:.2f}`, offset: `{offset:.4f}`, suma po: `{np.sum(y_normalized):.2f}`")
