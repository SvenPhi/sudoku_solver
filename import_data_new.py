# -*- coding: utf-8 -*-
"""
Created on Wed May 23 20:08:57 2018

@author: Sven

Dit package maakt data voor de zorgproductverdeling aan. Er is keuze tussen
dummy data en echte data.
"""

def maak_dummy_data(maanden = 36, instellingen = 8, diagnosen = 3, zorgproducten = 8):
    import numpy.random as nr
    import math as m
    import pandas as pd
    
    declaraties = pd.DataFrame({"maand_nr": [-1,-1],"AGB_ID": [-1,-1],
                                "Diagnosegroep_ID": [-1,-1],
                                "Zorgproduct_ID": [-1,-1],"Aantal": [0,0]})
    
    #Bepaal de gemiddelde waardes van ieder zorgproduct
    zorgproduct_mean = nr.normal(loc = 150, scale = 80, size = zorgproducten)
    #Als dit kleiner dan 0 is, zet de waarde op 0, omdat een zorgproduct nooit
    #minder dan één keer gedeclareerd is.
    for zp in zorgproduct_mean:
        if zp < 0: zorgproduct_mean[zorgproduct_mean.index(zp)] = 0
    
    #De factor voor de zorgproducten: hoe groot is iedere instelling
    agb_factor = nr.uniform(low = 0.5, high = 1.5, size = instellingen)
    
    
    
    for maand in range(1,maanden + 1):
        for agb in range(instellingen + 1):
                for dia in range(diagnosen):
                    for zorgproduct in range(zorgproducten):
                        aantal = np.random.binomial(n = 15,
                                                    p = 0.4,
                                                    size = 1) + 1
                        decl = pd.DataFrame({"maand_nr": maand,
                                             "AGB_ID": agb,
                                             "Diagnosegroep_ID": dia,
                                             "Zorgproduct_ID": zorgproduct,
                                             "Aantal": aantal})
                        declaraties = pd.concat([declaraties,decl], axis = 0, ignore_index = True)
                        
    declaraties = declaraties[declaraties.Maand_Nr != -1]
    #declaraties.reshape(declaraties.shape())
    return declaraties
            
    
def haal_data(start_periode, eind_periode):
    import pyodbc as pod
    import pandas as beertje
    
    query = """SELECT
                    Dense_Rank() OVER(PARTION BY NULL ORDER BY t.Jaar_Maand_Nr) AS maand_nr
                    ,ISNULL(f.AGB_ID_DECLARANT,0) AS AGB_ID
                    ,ind.DIAGNOSEGROEP_TRANSITIE_ID AS Diagnosegroep_ID
                    ,f.ZORGPRODUCT_ID AS Zorgproduct_ID
                    ,Count(*) AS AANTAL
                FROM Sophia_new.ziekenhuis_feit.ANL_FEIT_VERZ_DECLARATIE_DOT AS f
                INNER JOIN Sophia_new.generiek.ANL_DIM_TIJD AS t
                    ON f.BEGIN_DATUM_ID = t.DATUM_ID
                INNER JOIN Sophia_new.ziekenhuis_dim.ANL_DIM_DIAGNOSEGROEP_INDELING AS ind
                    ON f.DIAGNOSE_ID = ind.DIAGNOSE_ID
                WHERE 1=1
                    AND f.SOORT_REGEL = 1
                    AND t.Jaar_Maand_Nr BETWEEN {0} AND {1}
                GROUP BY
                    t.Jaar_Maand_Nr
                    ,ROLLUP(f.AGB_ID_DECLARANT)
                    ,ind.DIAGNOSEGROEP_TRANSITIE_ID
                    ,f.ZORGPRODUCT_ID;""".format(start_periode, eind_periode)
    