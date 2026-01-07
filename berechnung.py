import math

def CSB_berechnen(
        Bd_CSB_hom_ZT: float,       
        Bd_CSB_filt_ZT: float,      
        Q_d: float,                
        T: float,                   
        fs: float = 0.04,           
        fa: float = 0.03,           
        n: float = 0.5,             
        k_20: float = 0.0024,       
        hoehe_TK: float = 5.2,      
        A_spez: float = 120,        
        O_C_20: float = 1.02,       
        h_seg: float = 0.1,         
        q_A: float = 0.75           
    ):
    #Zulaufkonzentration aus Zulauffracht
    C_CSB_ZT = Bd_CSB_hom_ZT / Q_d * 1000

    #Fraktionierung
    S_CSB_ZT = Bd_CSB_filt_ZT/Q_d * 1000   
    X_CSB_ZT = C_CSB_ZT - S_CSB_ZT 
    S_CSB_inert_ZT = fs * C_CSB_ZT
    X_CSB_inert_ZT = fa * X_CSB_ZT
    
    #Abbaubarer gelöster CSB im Zulauf
    S_CSB_abb_ZT = S_CSB_ZT - S_CSB_inert_ZT + 0.5 * (X_CSB_ZT - X_CSB_inert_ZT)
    
    k_20_angepasst = k_20 * (5.2/hoehe_TK)*n #Anpassung des k_20-Wertes
    zaehler_s_csb_hoehe = 0
    ergebnis_liste = []
    ergebnis_liste = [[zaehler_s_csb_hoehe],[S_CSB_abb_ZT]]
    
    while(zaehler_s_csb_hoehe < hoehe_TK):

            #CSB-Abbau im Tropfkörper Velz-Gleichung
            exponent = (A_spez * k_20_angepasst * O_C_20*(T-20) * h_seg) / (q_A * n)
            S_CSB_abb_A = S_CSB_abb_ZT * math.exp(-exponent)
            
            zaehler_s_csb_hoehe = zaehler_s_csb_hoehe+h_seg
            
            S_CSB_abb_A = S_CSB_abb_A
            ergebnis_liste[0].extend([zaehler_s_csb_hoehe])
            ergebnis_liste[1].extend([S_CSB_abb_A])
            S_CSB_abb_ZT = S_CSB_abb_A

    return ergebnis_liste


def nitrifikation_segment(
    S_NH4_Z,
    Temp,
    A_spez,
    q_A,
    hv,
    S_CSB_abb_ZT,
    S_CSB_abb_A,
    O_N_10,
    j_N_max_10,
    N_saettigung,
    k_faktor,
    h_seg
    ): 
    
    temp_factor = O_N_10 ** (Temp - 10.0)                                   
    sat_factor = S_NH4_Z / (N_saettigung + S_NH4_Z)                        
    depth_factor = math.exp(-k_faktor * hv)                                 

    #Ammoniumstickstoff Konzentration im Ablauf des Tröpfchenkörpersegments

    delta_S = -(A_spez / (q_A * 24.0)) * j_N_max_10 * temp_factor * sat_factor * depth_factor
    delta_S = tab_G_B(S_CSB_abb_ZT)
     
    S_NH4_A = S_NH4_Z + delta_S * h_seg - (S_CSB_abb_ZT - S_CSB_abb_A) * 0.01
    
    if S_NH4_A < 0.0:
        S_NH4_A = 0.0
    
    return S_NH4_A
    
def tab_G_B(S_CSB_abb_segment):
    if S_CSB_abb_segment >= 100:
        return 0.0
    elif S_CSB_abb_segment <= 20:
        return 1
    else:
        return ((100 - S_CSB_abb_segment) / 80) ** 3


def nitrifikation_berechnen(
        werte_diagramm_csb, 
        B_d_NH4_ZT: float,          
        Q_d: float,                
        T: float,                   
        j_n_max_10: float = 1.8,   
        N: float = 1.75,            
        k: float = 0.11,           
        O_N_10: float = 1.02,       
        h_v: float = 0.0,           
        A_spez: float = 120,        
        h_seg: float = 0.1,         
        q_A: float = 0.39           
    ):
    S_NH4_Z = B_d_NH4_ZT/Q_d*1000
    werte_diagramm_gesamt = [
        werte_diagramm_csb[0][:],   
        werte_diagramm_csb[1][:],   
        [S_NH4_Z]                   
    ]
    hv = 0.0
    for i in range(1, len(werte_diagramm_csb[0])):
        h_v = werte_diagramm_csb[0][i]
        S_CSB_abb_ZT = werte_diagramm_csb[1][i-1]
        S_CSB_abb_A = werte_diagramm_csb[1][i]
        if S_CSB_abb_ZT>=100.0 and S_CSB_abb_A<100.0:
            hv = h_seg
        S_NH4_Z = werte_diagramm_gesamt[2][i-1]
        werte_diagramm_gesamt[2].extend([nitrifikation_segment(
            S_NH4_Z, T, A_spez, q_A, hv, S_CSB_abb_ZT, S_CSB_abb_A, O_N_10, j_n_max_10, N, k, h_seg)])
        if hv > 0.0:
            hv += h_seg
    return werte_diagramm_gesamt

def reinigungsleistung_berechnen(werte_diagramm_gesamt):
    S_CSB_ZT = werte_diagramm_gesamt[1][0]
    S_CSB_A_end = werte_diagramm_gesamt[1][-1]
    S_NH4_Z = werte_diagramm_gesamt[2][0]
    S_NH4_A_end = werte_diagramm_gesamt[2][-1]

    csb_absolut = S_CSB_ZT - S_CSB_A_end
    csb_relativ = (csb_absolut / S_CSB_ZT) * 100.0

    nh4_absolut = S_NH4_Z - S_NH4_A_end
    nh4_relativ = (nh4_absolut / S_NH4_Z) * 100.0

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
