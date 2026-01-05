import math

#Eingaben CSB:
Bd_CSB_hom_ZT = float(input("Tagesfracht des CSB homogenisiert in [kg/d]:"))
Q_d = float(input("Trockenwetterabfluss im Jahresmittel in [m³/d]:"))
Bd_CSB_filt_ZT = float(input("Tagesfracht des CSB filtriert in [kg/d]:"))
T = float(input("Abwassertemperatur in [°C]:"))

#Eingaben Nitrifikation:
B_d_NH4_ZT = float(input("NH4-N-Konzentration im Zulauf zum Tropfkörper in [kg/d]:"))



def CSB_berechnen():
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


#Nitrifikation

#Gujer und Boller Gleichung
#Anwendung der Gujer-und-Boller-Gleichung im Übergangsbereich 

def tab_G_B(S_CSB_abb_segment):
    if S_CSB_abb_segment >= 100:
        return 0.0
    elif S_CSB_abb_segment <= 20:
        return 1
    else:
        return ((100 - S_CSB_abb_segment) / 80) ** 3

def nitrifikation_berechnen(S_CSB_abb_ZT, S_CSB_abb_A, S_NH4_Z_E):
    temp_faktor = O_N_10 ** (T - 10)
    saettigung_faktor = S_NH4_Z_E / N + S_NH4_Z_E

    delta_S_NH4_E = -(A_spez / (q_A * 24)) * j_n_max_10 * (temp_faktor) * (saettigung_faktor) * math.exp(-k * h_v)

    S_NH4_A_E = S_NH4_Z_E + delta_S_NH4_E + h_seg - (S_CSB_abb_ZT - S_CSB_abb_A) * 0.01
    S_NH4_ZT = (B_d_NH4_ZT / Q_d) * 1000


    return S_NH4_A_E

def reinigungsleistung_berechnen(C_zulauf, C_ablauf):
    delta_C = C_zulauf - C_ablauf
    if C_zulauf < 0:
        reinigungsleistung_berechnen = 0
    else:
        reinigungsgrad_prozent = ((C_zulauf - C_ablauf) / C_zulauf) * 100
    
    
#Annahmen CSB Abbau:
fs = 0.05 #inerte Fraktion im Zulauf
fa = 0.30 #inerte Fraktion im partikulären CSB
n = 0.5 #hydraulischer Koeffizient
k_20 = 0.0024 #Reaktionskonstante
hoehe_TK = 5.2 #höhe Tropfkörper
A_spez = 125 #spezifische Oberfläche des Tropfkörpers in [m²/m³]
O_C_20 = 1.03 #Temperaturkoeffizient
h_seg = 0.1 #Segmenthöhe in [m]
q_A = 0.39 #Hydraulische Beschickung in [m³/m²*h]
h_v= 0.0 #

#Annahmen Nitrifikation:
j_n_max_10 = 1.8 #Reaktionsrate bei 10°C in [g NH4-N/m²*d]
N = 2 #Sättigungskonstante in [g NH4-N/m³] #liegt zwischen 1 und 2
k = 0.11 #Faktor K
O_N_10 = 1.02 #Temperaturkorrekturfaktor
