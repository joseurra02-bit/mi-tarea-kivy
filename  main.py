import os, sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window

Window.clearcolor = (0.11, 0.11, 0.11, 1)

class BalanceGalletasApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs); self.texto_impresion = ""

    def mostrar_error(self, t, m):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        lbl = Label(text=m, halign='center', valign='middle')
        lbl.bind(size=lambda s, w: setattr(s, 'text_size', s.size))
        btn = Button(text="Entendido", size_hint_y=None, height=45)
        box.add_widget(lbl); box.add_widget(btn)
        pop = Popup(title=t, content=box, size_hint=(0.8, 0.4))
        btn.bind(on_press=pop.dismiss); pop.open()

    def build(self):
        root = ScrollView(size_hint=(1, 1))
        lay = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        lay.bind(minimum_height=lay.setter('height'))
        lay.add_widget(Label(text="BALANCE DE MASA PARA GALLETAS", font_size='14sp', bold=True, color=(0.2, 0.6, 0.86, 1), size_hint_y=None, height=35))
        self.lbl_p = Label(text="Proteína: --%"); self.lbl_g = Label(text="Grasa: --%")
        self.lbl_a = Label(text="Azúcar: --%"); self.lbl_l = Label(text="Lácteos: --%")
        self.lbl_h = Label(text="Hidrat.: --%", font_size='14sp', bold=True, size_hint_y=None, height=30)
        f_nut = GridLayout(cols=2, spacing=5, size_hint_y=None, height=70)
        for l in [self.lbl_p, self.lbl_g, self.lbl_a, self.lbl_l]:
            l.bind(size=lambda s, w: setattr(s, 'text_size', s.size)); f_nut.add_widget(l)
        lay.add_widget(f_nut); lay.add_widget(self.lbl_h)
        f_lote = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        self.entry_g = TextInput(text="1000", input_filter='float', multiline=False, size_hint_y=None, height=40)
        f_lote.add_widget(Label(text="Lote solicitado (g):", bold=True)); f_lote.add_widget(self.entry_g); lay.add_widget(f_lote)
        lay.add_widget(Label(text=" % Secundarios ", bold=True, font_size='12sp', color=(0.2, 0.6, 0.86, 1), size_hint_y=None, height=30))
        
        # Aumentamos el alto a 320 para que la vainilla tenga espacio físico y aparezca en pantalla
        f_ing = GridLayout(cols=2, spacing=10, size_hint_y=None, height=320)
        self.inputs = {}
        ing_sec = ["Maicena", "Cacao", "Leche", "Marga", "Aceite", "Papelon", "Vainilla"]
        for name in ing_sec:
            lbl = Label(text=f"{name}:", halign='left'); lbl.bind(size=lambda s, w: setattr(s, 'text_size', s.size))
            txt = TextInput(text="0.0", input_filter='float', multiline=False, size_hint_y=None, height=40)
            f_ing.add_widget(lbl); f_ing.add_widget(txt); self.inputs[name.lower()] = txt
        lay.add_widget(f_ing)
        
        b_calc = Button(text="CALCULAR", size_hint_y=None, height=50, background_color=(0.18, 0.8, 0.44, 1))
        b_calc.bind(on_press=self.calcular_balance); lay.add_widget(b_calc)
        b_imp = Button(text="🖨️ IMPRIMIR RECETA", size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.86, 1))
        b_imp.bind(on_press=self.imprimir_receta); lay.add_widget(b_imp)
        self.txt_pesos = TextInput(text="El reporte aparecerá aquí...", readonly=True, font_size='11sp', size_hint_y=None, height=350)
        lay.add_widget(self.txt_pesos); root.add_widget(lay)
        return root
    def calcular_balance(self, instance):
        try:
            g_lote = float(self.entry_g.text)
            s_ma = float(self.inputs['maicena'].text); s_ca = float(self.inputs['cacao'].text)
            s_le = float(self.inputs['leche'].text); s_mr = float(self.inputs['marga'].text)
            s_ac = float(self.inputs['aceite'].text); s_pa = float(self.inputs['papelon'].text)
            s_va = float(self.inputs['vainilla'].text)
            i_har = 100.0 - (s_ma + s_ca + s_le); i_man = 60.0 - (s_mr + s_ac)
            i_azu = 50.0 - s_pa; i_hue = 20.0 - s_va
            if i_har < 0 or i_man < 0 or i_azu < 0 or i_hue < 0:
                self.mostrar_error("Error", "¡Un secundario superó a su Patrón!"); return
            receta = {
                "Harina": i_har, "Maicena": s_ma, "Cacao polvo": s_ca, "Leche polvo": s_le,
                "Manteca veg.": i_man, "Margarina": s_mr, "Aceite": s_ac, "Azúcar común": i_azu,
                "Papelón": s_pa, "Huevos": i_hue, "Vainilla": s_va, "Polvo hornear": 0.5, "Bicarbonato": 0.5, "Sal": 0.3
            }
            suma = sum(receta.values())
            tabla = {
                "Harina": [0.110, 0.012, 0.003, 0.000, 0.130], "Maicena": [0.003, 0.000, 0.000, 0.000, 0.120],
                "Cacao polvo": [0.200, 0.110, 0.010, 0.000, 0.050], "Leche polvo": [0.260, 0.260, 0.380, 0.960, 0.040],
                "Manteca veg.": [0.000, 0.990, 0.000, 0.000, 0.005], "Margarina": [0.005, 0.3465, 0.000, 0.010, 0.6428],
                "Aceite": [0.000, 1.000, 0.000, 0.000, 0.000], "Azúcar común": [0.000, 0.000, 1.000, 0.000, 0.001],
                "Papelón": [0.000, 0.000, 0.850, 0.000, 0.060], "Huevos": [0.126, 0.105, 0.007, 0.000, 0.750],
                "Vainilla": [0.000, 0.000, 0.050, 0.000, 0.650], "Polvo hornear": [0.000, 0.000, 0.000, 0.000, 0.050],
                "Bicarbonato": [0.000, 0.000, 0.000, 0.000, 0.010], "Sal": [0.000, 0.000, 0.000, 0.000, 0.002]
            }
            acum = [0.0, 0.0, 0.0, 0.0, 0.0]
            for ing, p_pan in receta.items():
                pct = (p_pan / suma) * 100.0
                for i in range(5): acum[i] += (pct / 100.0) * tabla[ing][i]
            nut = [v * 100.0 for v in acum]
            self.lbl_p.text = f"Proteína: {nut[0]:.2f}%"; self.lbl_g.text = f"Grasa: {nut[1]:.2f}%"
            self.lbl_a.text = f"Azúcar: {nut[2]:.2f}%"; self.lbl_l.text = f"Lácteos: {nut[3]:.2f}%"
            hid_real = nut[4]
            if 7.0 <= hid_real <= 25.0:
                self.lbl_h.text = f"Hidrat.: {hid_real:.2f}% (✅)"; self.lbl_h.color = (0.18, 0.8, 0.44, 1)
            else:
                self.lbl_h.text = f"Hidrat.: {hid_real:.2f}% (❌)"; self.lbl_h.color = (0.9, 0.3, 0.23, 1)
            rep = "========================================\n     HOJA DE PESAJE DE GALLETAS         \n========================================\n"
            rep += f"Lote solicitado: {g_lote:.1f} g\n----------------------------------------\n"
            for ing, p_pan in receta.items():
                pct = (p_pan / suma) * 100.0; gramos = (pct / 100.0) * g_lote
                if gramos > 0: rep += f" * {ing.ljust(13)}: {gramos:7.1f} g ({pct:4.1f}% real)\n"
            rep += f"----------------------------------------\nComposición de la masa:\n"
            rep += f" -> Proteína: {nut[0]:.2f}%\n -> Grasa:    {nut[1]:.2f}%\n -> Azúcar:   {nut[2]:.2f}%\n -> Lácteos:  {nut[3]:.2f}%\n -> Hidrat.:  {hid_real:.2f}%\n========================================\n"
            self.txt_pesos.text = rep; self.texto_impresion = rep
        except ValueError:
            self.mostrar_error("Error", "Ingresa números válidos.")

    def imprimir_receta(self, instance):
        if self.texto_impresion == "":
            self.mostrar_error("Imprimir", "Haz clic en 'CALCULAR' primero."); return
        try:
            r_comp = os.path.join(self.user_data_dir, "receta_galletas.txt")
            with open(r_comp, "w", encoding="utf-8") as f: f.write(self.texto_impresion)
            self.mostrar_error("🖨️ Guardado", f"¡Receta guardada con éxito!\n\nArchivo guardado en:\n{r_comp}")
        except Exception as e: self.mostrar_error("Error", f"Fallo: {e}")

if __name__ == '__main__':
    BalanceGalletasApp().run()
