import math

def runden(wert, dezimalstellen):
    epsilon = 1e-10 
    return round(wert + epsilon, dezimalstellen)

def CSB_berechnen(
        Bd_CSB_hom_ZT: float,       # (variable) Tagesfracht des CSB homogenisiert in [kg/d]
        Bd_CSB_filt_ZT: float,      # (variable) Tagesfracht des CSB filtriert in [kg/d]
        Q_d: float,                 # (variable) Trockenwetterabfluss im Jahresmittel in [m³/d]
        T: float,                   # (variable) Abwassertemperatur in [°C]
        fs: float = 0.05,           # inerte Fraktion im Zulauf
        fa: float = 0.30,           # inerte Fraktion im partikulären CSB
        n: float = 0.5,             # hydraulischer Koeffizient
        k_20: float = 0.0024,       # Reaktionskonstante
        hoehe_TK: float = 5.2,      # höhe Tropfkörper
        A_spez: float = 125,        # spezifische Oberfläche des Tropfkörpers in [m²/m³]
        O_C_20: float = 1.03,       # Temperaturkoeffizient
        h_seg: float = 0.1,         # Segmenthöhe in [m]
        q_A: float = 0.39           # Hydraulische Beschickung in [m³/m²*h]
    ):
    #Zulaufkonzentration aus Zulauffracht
    C_CSB_ZT = Bd_CSB_hom_ZT / Q_d * 1000

    #Fraktionierung
    
    if Bd_CSB_filt_ZT == 0:
        S_CSB_ZT =  C_CSB_ZT
    else:
        S_CSB_ZT = runden(Bd_CSB_filt_ZT/Q_d * 1000,2) #gelöst
    
    S_CSB_ZT = runden(Bd_CSB_filt_ZT/Q_d * 1000,2) #gelöst
    
    
    X_CSB_ZT = C_CSB_ZT - S_CSB_ZT #partikulär
    
    S_CSB_inert_ZT = runden(fs * C_CSB_ZT,2)
    X_CSB_inert_ZT = runden(fa * X_CSB_ZT,2)
    
    #Abbaubarer gelöster CSB im Zulauf
    S_CSB_abb_ZT = runden(S_CSB_ZT - S_CSB_inert_ZT + 0.5 * (X_CSB_ZT - X_CSB_inert_ZT),2)
    
    k_20_angepasst = runden(k_20 * (5.2/hoehe_TK)*n, 5)  #Anpassung des k_20-Wertes an die Tropfkörperhöhe


    zaehler_s_csb_hoehe = 0
    ergebnis_liste = []
    ergebnis_liste = [[zaehler_s_csb_hoehe],[S_CSB_abb_ZT]]
    
    while(zaehler_s_csb_hoehe < hoehe_TK):

            #CSB-Abbau im Tropfkörper Velz-Gleichung
            exponent = (A_spez * k_20_angepasst * O_C_20*(T-20) * h_seg) / (q_A * n)
            S_CSB_abb_A = S_CSB_abb_ZT * math.exp(-exponent)
            
            zaehler_s_csb_hoehe = runden(zaehler_s_csb_hoehe+h_seg, 1)
            
            S_CSB_abb_A = runden(S_CSB_abb_A, 1)
            ergebnis_liste[0].extend([zaehler_s_csb_hoehe])
            ergebnis_liste[1].extend([S_CSB_abb_A])
            S_CSB_abb_ZT = runden(S_CSB_abb_A, 1)

    return ergebnis_liste

#Gujer und Boller Gleichung
def calc_w(S_CSB_abb_segment):  # Gujer-und-Boller Gewichtung
    if S_CSB_abb_segment >= 100.0:
        return 0.0
    elif S_CSB_abb_segment <= 20.0:
        return 1.0
    else:
        return ((100.0 - S_CSB_abb_segment) / 80.0) ** 3

def nitrifikation_segment(S_NH4_Z, Temp, A_spez, q_A, hv, S_CSB_abb_ZT, S_CSB_abb_A, O_N_10, j_N_max_10, N_saettigung, k_faktor, h_seg): 
    temp_factor = O_N_10 ** (Temp - 10.0) #Temperaturkoeffizient 10°
    sat_factor = S_NH4_Z / (N_saettigung + S_NH4_Z) #Sättigungsfaktor
    depth_factor = math.exp(-k_faktor * hv) #Abnahme der wirksamen Nitrifikation mit zunehmender Tropfkörperhöhe

    #Konzentration des Ammoniumstickstoffs im Ablauf des Tröpfchenkörpersegments
    delta_S = -(A_spez / (q_A * 24.0)) * j_N_max_10 * temp_factor * sat_factor * depth_factor
    delta_S *= calc_w(S_CSB_abb_ZT)
     
    S_NH4_A = S_NH4_Z + delta_S * h_seg - (S_CSB_abb_ZT - S_CSB_abb_A) * 0.01
    
    if S_NH4_A < 0.0:
        S_NH4_A = 0.0
    
    return S_NH4_A
    
#def s_nh4_abb_berechen(werte_diagramm_csb, Bd_NH4_ZT, Temp, A_spez, q_A, O_N_10, j_N_max_10, N_saettigung, k_faktor, h_seg, Q_d):
def nitrifikation_berechnen(
        werte_diagramm_csb, 
        B_d_NH4_ZT: float,          # (variable) NH4-N-Konzentration im Zulauf zum Tropfkörper in [kg/d]
        Q_d: float,                 # (variable) Trockenwetterabfluss im Jahresmittel in [m³/d]
        T: float,                   # (variable) Abwassertemperatur in [°C]
        j_n_max_10: float = 1.8,    # Reaktionsrate bei 10°C in [g NH4-N/m²*d]
        N: float = 2,               # Sättigungskonstante in [g NH4-N/m³] #liegt zwischen 1 und 2
        k: float = 0.11,            # Faktor K
        O_N_10: float = 1.02,       # Temperaturkorrekturfaktor
        h_v: float = 0.0,           # Startpunkt Höhe
        A_spez: float = 125,        # spezifische Oberfläche des Tropfkörpers in [m²/m³]
        h_seg: float = 0.1,         # Segmenthöhe in [m]
        q_A: float = 0.39           # Hydraulische Beschickung in [m³/m²*h]
    ):
    S_NH4_Z = B_d_NH4_ZT/Q_d*1000
    werte_diagramm_gesamt = [
        werte_diagramm_csb[0][:],   # Kopie der Höhen
        werte_diagramm_csb[1][:],   # Kopie der CSB-Werte
        [S_NH4_Z]                   # Erstelle die NEUE Liste [2] mit dem Startwert
    ]
    hv = 0.0
    for i in range(1, len(werte_diagramm_csb[0])):
        h_aktuell = werte_diagramm_csb[0][i]
        S_CSB_abb_ZT = werte_diagramm_csb[1][i-1]
        S_CSB_abb_A = werte_diagramm_csb[1][i]
        if S_CSB_abb_ZT>=100.0 and S_CSB_abb_A<100.0:
            hv = h_seg
        S_NH4_Z = werte_diagramm_gesamt[2][i-1]
        werte_diagramm_gesamt[2].extend([nitrifikation_segment(
            S_NH4_Z, T, A_spez, q_A, hv, S_CSB_abb_ZT, S_CSB_abb_A, O_N_10, j_n_max_10, N, k, h_seg)])
        if hv > 0.0:
            hv += runden(h_seg,1)
    return werte_diagramm_gesamt

def reinigungsleistung_berechnen(werte_diagramm_gesamt):
    S_CSB_ZT = werte_diagramm_gesamt[1][0]
    S_CSB_A_end = werte_diagramm_gesamt[1][-1]
    S_NH4_Z = werte_diagramm_gesamt[2][0]
    S_NH4_A_end = werte_diagramm_gesamt[2][-1]

    csb_absolut = runden(S_CSB_ZT - S_CSB_A_end, 1)
    csb_relativ = runden((csb_absolut / S_CSB_ZT) * 100.0, 1)

    nh4_absolut = runden(S_NH4_Z - S_NH4_A_end, 1)
    nh4_relativ = runden((nh4_absolut / S_NH4_Z) * 100.0, 1)

    return {
        "CSB-Reinigung": {
            "absolut": csb_absolut,
            "relativ": csb_relativ
        },
        "NH4-N-Reinigung": {
            "absolut": nh4_absolut,
            "relativ": nh4_relativ
        }
    }


def tab_G_B(S_CSB_abb_segment):
    if S_CSB_abb_segment >= 100:
        return 0.0
    elif S_CSB_abb_segment <= 20:
        return 1
    else:
        return ((100 - S_CSB_abb_segment) / 80) ** 3



