import math

#Eingaben
Bd_CSB_hom_ZT = float(input("Tagesfracht des CSB homogenisiert in [kg/d]:"))
Q_d = float(input("Trockenwetterabfluss im Jahresmittel in [m³/d]:"))
Bd_CSB_filt_ZT = float(input("Tagesfracht des CSB filtriert in [kg/d]:"))


#Annahmen:
fs = 0.05 #inerte Fraktion im Zulauf
fa = 0.30 #inerte Fraktion im partikulären CSB
n = 0.5 #keine AHnung, ist so
k_20 = 0.0024 #Reaktionskonstante
höhe_TK = 5.2 #höhe Tropfkörper

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
k_20_angepasst = k_20 * (5.2 / höhe_TK) ** n 




















#Prints
print("gelöster inerter Anteil des CSB",(S_CSB_inert_ZT))
print("Zulaufkonzentration",(C_CSB_ZT))
print(X_CSB_inert_ZT)



