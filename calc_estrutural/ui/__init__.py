"""Camada de apresentação (Streamlit) do Calc Estrutural.

Um módulo por elemento (laje, viga, pilar, muro, reservatorio, piscina,
viga_parede), cada um expondo `render()` que monta as 5 abas do elemento.
Dependências apontam só para dentro: ui -> dimensionamento / relatorio.
"""
