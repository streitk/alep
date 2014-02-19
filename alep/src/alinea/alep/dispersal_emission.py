""" Gather different strategies for modeling emission of fungus propagules, 
    first step of dispersal.
"""

# Imports #########################################################################
from alinea.alep.architecture import get_total_leaf_area
from alinea.alep.septoria import SeptoriaDU
from alinea.alep.powdery_mildew import PowderyMildewDU
from math import exp

# Septoria rain emission ##########################################################
class SeptoriaRainEmission:
    """ Template class for a model of emission of dispersal units by rain 
        that complies with the guidelines of Alep.
    
    Emission is the first step of dispersal, before transport. A class for a model 
    of emission must include a method 'get_dispersal_units'. In this example, the 
    number of dispersal units emitted is calculated according to the equations of
    Rapilly and Jolivet (1976).
    """
    
    def __init__(self, domain_area=None):
        """ Initialize the model with fixed parameters.
        
        Parameters
        ----------
        domain_area: float
            Domain area of the canopy stand
        """
        self.domain_area = domain_area
        
    def get_dispersal_units(self, g, fungus_name="septoria", label='LeafElement'):
        """ Compute emission of dispersal units by rain splash on wheat.
        
        Parameters
        ----------
        g: MTG
            MTG representing the canopy (and the soil)
        fungus_name: str
            Name of the fungus
                    
        Returns
        -------
        dispersal_units : dict([leaf_id, list of dispersal units])
            Dispersal units emitted by leaf.
        """
        k_wheat = 0.65
        
        # Compute total leaf area
        total_area = get_total_leaf_area(g, label=label)
        
        # Compute intercept with Beer Lambert
        intercept = 1 - exp(-k_wheat*total_area*10**-4/self.domain_area)
        # intercept = 1 - exp(-k_wheat*total_area*10**-4)
        
        # Get lesions
        les = {k:[l for l in v if l.fungus.name is fungus_name and l.is_sporulating()] 
                    for k, v in g.property('lesions').iteritems()} 
        
        # Compute total sporulating area
        total_spo = sum([l.surface_spo for v in les.values() for l in v])
        # tot_fraction_spo = total_spo/(total_area/self.domain_area) if (total_area/self.domain_area)>0. else 0.
        tot_fraction_spo = total_spo/total_area if total_area>0. else 0.
        
        DU = {}
        for vid, l in les.iteritems():
            for lesion in l:
                # Compute number of dispersal units emitted by lesion
                leaf = g.node(vid)
                total_DU_leaf = 0.36 * 6.19e7 * intercept * tot_fraction_spo * leaf.rain_intensity * self.domain_area
                
                if lesion.is_stock_available(leaf):
                    initial_stock = lesion.stock_spores
                    stock_available = int(lesion.stock_spores*2/3.)
                    contribution = lesion.surface_spo/total_spo if total_spo>0. else 0.
                    nb_DU_lesion = int(contribution * total_DU_leaf)
                    
                    # Distribute spores into dispersal units
                    nb_spores_by_DU = 10
                    nb_DU_lesion = min(nb_DU_lesion, stock_available/nb_spores_by_DU)
                    
                    SeptoriaDU.fungus = lesion.fungus
                    emissions = [SeptoriaDU(nb_spores = nb_spores_by_DU, status='emitted', 
                                 position=lesion.position) for i in range(nb_DU_lesion)]

                    # Update stock of spores of the lesion
                    nb_spores_emitted = nb_DU_lesion*nb_spores_by_DU
                    lesion.reduce_stock(nb_spores_emitted)
                    
                    # Update empty surface on lesion
                    lesion.update_empty_surface(nb_spores_emitted, initial_stock)
                    
                    if vid not in DU:
                        DU[vid] = []
                    DU[vid] += emissions
        return DU
        
# Septoria rain emission ##########################################################
class PowderyMildewWindEmission:
    """ Template class for a model of emission of dispersal units by wind 
        that complies with the guidelines of Alep.
    
    Emission is the first step of dispersal, before transport. A class for a model 
    of emission must include a method 'get_dispersal_units'. In this example, the 
    number of dispersal units emitted is calculated according to the equations of
    Willocquet and Clerjeau (1998).
    """
    
    def __init__(self):
        """ Initialize the model with fixed parameters.
        """
        pass
        
    def get_dispersal_units(self, g, fungus_name="powdery_mildew", label='lf'):
        """ Compute emission of dispersal units by rain splash on wheat.
        
        Parameters
        ----------
        g: MTG
            MTG representing the canopy (and the soil)
        fungus_name: str
            Name of the fungus
                    
        Returns
        -------
        dispersal_units : dict([leaf_id, list of dispersal units])
            Dispersal units emitted by leaf.
        """
        a = 0.71
        b = -5.8
        r = 0.41
        treshold_to_empty = 1
        
        # Get lesions
        lesions = {k:[l for l in les if l.fungus.name is fungus_name and l.is_sporulating()] 
                    for k, les in g.property('lesions').iteritems()} 
        
        DU = {}
        for vid, l in lesions.iteritems():
            leaf = g.node(vid)
            wind_speed = leaf.wind_speed
            for lesion in l:
                emissions = []
                stock = lesion.stock_spores
                if stock > 0.:
                    # Dispersal rate
                    dispersal_rate = exp(r*wind_speed+b) / (1+exp(r*wind_speed+b))
                    # Number of spores emitted : One only spore by DU
                    nb_DU_emitted = int(dispersal_rate * stock)
                    
                    if nb_DU_emitted > 0 :
                        # Return emissions
                        PowderyMildewDU.fungus = lesion.fungus
                        emissions = [PowderyMildewDU(nb_spores=1, status='emitted',
                                                position=lesion.position) for i in range(nb_DU_emitted)]
                        # Update stock of spores                       
                        lesion.reduce_stock(nb_spores_emitted = nb_DU_emitted)

                        if vid not in DU:
                            DU[vid] = []
                        DU[vid] += emissions
        return DU