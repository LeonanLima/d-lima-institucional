"""Coloca a raiz do calc_estrutural no sys.path para os testes importarem
os pacotes dimensionamento/, normas/, relatorio/ como top-level."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
