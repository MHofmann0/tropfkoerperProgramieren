import math

#Eingaben
Bd_CSB_hom_ZT = float(input("Tagesfracht des CSB homogenisiert in [kg/d]:"))
Q_d = float(input("Trockenwetterabfluss im Jahresmittel in [m³/d]:"))
Bd_CSB_filt_ZT = float(input("Tagesfracht des CSB filtriert in [kg/d]:"))
T = float(input("Abwassertemperatur in [°C]:"))

#Annahmen:
fs = 0.05 #inerte Fraktion im Zulauf
fa = 0.30 #inerte Fraktion im partikulären CSB
n = 0.5 #hydraulischer Koeffizient
k_20 = 0.0024 #Reaktionskonstante
hoehe_TK = 5.2 #höhe Tropfkörper
A_spez = 125 #spezifische Oberfläche des Tropfkörpers in [m²/m³]
O_C_20 = 1.03 #Temperaturkoeffizient
h_seg = 0.1 #Segmenthöhe in [m]
q_A = 0.39 #Hydraulische Beschickung in [m³/m²*h]


#Zulaufkonzentration aus Zulauffracht
C_CSB_ZT = Bd_CSB_hom_ZT /Q_d * 1000
S_CSB_ZT = Bd_CSB_filt_ZT / Q_d * 1000

#Fraktionierung
S_CSB_inert_ZT = fs * C_CSB_ZT

X_CSB_ZT = C_CSB_ZT - S_CSB_ZT
X_CSB_inert_ZT = fa * X_CSB_ZT

#Abbaubarer gelöster CSB im Zulauf
X_CSB_abb_ZT = X_CSB_ZT - X_CSB_inert_ZT
S_CSB_abb_ZT = S_CSB_abb_ZT + 0.5 * X_CSB_abb_ZT

#Anpassung des k-20 Wertes
k_20_angepasst = k_20 * (5.2 / hoehe_TK) ** n 


zaehler_S_CSB_hoehe = 0
ergebnis_liste = []
ergebnis_liste = [[zaehler_S_CSB_hoehe], [S_CSB_abb_ZT]]

while(zaehler_S_CSB_hoehe < hoehe_TK):
    #modifizierte Velz-Gleichung
    exponent =  (A_spez * k_20_angepasst * O_C_20 ** (T-20) + h_seg) /(q_A ** n)
    S_SCB_abb_AT = S_CSB_abb_ZT * math.exp(-exponent)
    
    zaehler_S_CSB_hoehe = zaehler_S_CSB_hoehe + h_seg
    
    ergebnis_liste[0].append(zaehler_S_CSB_hoehe)
    ergebnis_liste[1].append(S_SCB_abb_AT)

    S_CSB_abb_ZT = S_SCB_abb_AT

return ergebnis_liste

















#Prints
print("gelöster inerter Anteil des CSB",(S_CSB_inert_ZT))
print("Zulaufkonzentration",(C_CSB_ZT))
print(X_CSB_inert_ZT)



