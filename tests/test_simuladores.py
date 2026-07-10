"""Casos de prueba de los dos simuladores (ejecutar con: python -m pytest -q).

También funciona con unittest: python -m unittest tests.test_simuladores
"""

import unittest

from src.memoria import AdministradorMemoria, Proceso, obtener_estrategia
from src.traduccion import Paginacion, Segmentacion, Segmento


class TestAsignacionMemoria(unittest.TestCase):
    def test_first_fit_usa_primer_hueco(self):
        admin = AdministradorMemoria(1000, obtener_estrategia("first_fit"))
        admin.asignar(Proceso("P1", 200))
        admin.asignar(Proceso("P2", 300))
        admin.liberar("P1")  # hueco de 200 al inicio
        res = admin.asignar(Proceso("P3", 100))
        self.assertTrue(res.exito)
        # First Fit debe colocar P3 en la dirección 0 (primer hueco).
        self.assertEqual(res.bloque.inicio, 0)

    def test_best_fit_elige_hueco_mas_ajustado(self):
        admin = AdministradorMemoria(1000, obtener_estrategia("best_fit"))
        admin.asignar(Proceso("P1", 100))
        admin.asignar(Proceso("P2", 300))
        admin.asignar(Proceso("P3", 100))
        admin.liberar("P1")  # hueco 100 en dir 0
        admin.liberar("P3")  # hueco 100 en dir 400
        # Quedan dos huecos de 100 y uno grande al final.
        res = admin.asignar(Proceso("P4", 100))
        self.assertTrue(res.exito)
        self.assertEqual(res.bloque.tamano, 100)

    def test_worst_fit_usa_hueco_mas_grande(self):
        admin = AdministradorMemoria(1000, obtener_estrategia("worst_fit"))
        admin.asignar(Proceso("P1", 100))
        admin.liberar("P1")
        res = admin.asignar(Proceso("P2", 50))
        # Worst Fit debe usar el hueco grande restante, no un hueco pequeño.
        self.assertTrue(res.exito)

    def test_fragmentacion_interna_por_alineacion(self):
        admin = AdministradorMemoria(512, obtener_estrategia("first_fit"), alineacion=32)
        admin.asignar(Proceso("A", 100))  # se redondea a 128 -> 28 de frag interna
        self.assertEqual(admin.fragmentacion_interna, 28)

    def test_no_cabe_por_fragmentacion_externa(self):
        admin = AdministradorMemoria(300, obtener_estrategia("first_fit"))
        admin.asignar(Proceso("P1", 100))
        admin.asignar(Proceso("P2", 100))
        admin.asignar(Proceso("P3", 100))
        admin.liberar("P1")
        admin.liberar("P3")  # 200 libres pero en huecos separados de 100
        res = admin.asignar(Proceso("P4", 150))
        self.assertFalse(res.exito)
        self.assertEqual(admin.fragmentacion_externa, 100)

    def test_fusion_de_huecos_al_liberar(self):
        admin = AdministradorMemoria(300, obtener_estrategia("first_fit"))
        admin.asignar(Proceso("P1", 100))
        admin.asignar(Proceso("P2", 100))
        admin.liberar("P1")
        admin.liberar("P2")
        # Tras liberar ambos, debe quedar un único hueco de 300.
        self.assertEqual(len(admin.bloques), 1)
        self.assertEqual(admin.bloques[0].tamano, 300)


class TestPaginacion(unittest.TestCase):
    def setUp(self):
        self.sim = Paginacion(64, 32, 8, {0: 3, 1: 1, 2: 0, 5: 2})

    def test_traduccion_correcta(self):
        # dir 9 -> página 1, offset 1 -> marco 1 -> 1*8+1 = 9
        res = self.sim.traducir(9)
        self.assertTrue(res.exito)
        self.assertEqual(res.numero_pagina, 1)
        self.assertEqual(res.desplazamiento, 1)
        self.assertEqual(res.direccion_fisica, 9)

    def test_fallo_de_pagina(self):
        # dir 30 -> página 3, no está en la tabla
        res = self.sim.traducir(30)
        self.assertFalse(res.exito)

    def test_direccion_fuera_de_rango(self):
        res = self.sim.traducir(64)
        self.assertFalse(res.exito)


class TestSegmentacion(unittest.TestCase):
    def setUp(self):
        self.sim = Segmentacion(
            2000,
            [
                Segmento(0, 100, 500, "codigo"),
                Segmento(1, 700, 300, "datos"),
            ],
        )

    def test_acceso_valido(self):
        res = self.sim.traducir(0, 50)
        self.assertTrue(res.exito)
        self.assertEqual(res.direccion_fisica, 150)

    def test_violacion_de_limite(self):
        res = self.sim.traducir(0, 500)  # límite es 500 -> inválido
        self.assertFalse(res.exito)

    def test_segmento_inexistente(self):
        res = self.sim.traducir(9, 0)
        self.assertFalse(res.exito)


if __name__ == "__main__":
    unittest.main()
