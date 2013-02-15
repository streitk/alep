""" Define the protocol between plant architecture and lesions """

import random

def initiate(g, 
             dispersal_units_stock, 
             initiation_model, 
             label="LeafElement"):
    """ Allocates dispersal units (objects) on elements of the MTG according to initiation_model 

    :Parameters:
      - `g` : MTG representing the canopy (and the soil).
      - `dispersal_units_stock` : source of dispersal units to disperse in the scene.
      - `initiation_model` : model that allows positioning each DU in stock on g.

    :Example:
      >>> g = MTG()
      >>> stock = [SeptoriaDU(fungus = septoria(), nbSpores=random.randint(1,100), nature='emitted') for i in range(100)]
      >>> inoculator = RandomInoculation()
      >>> initiate(g, stock, inoculator)
      >>> return g
    """
    # Allocation of stock of inoculum
    initiation_model.disperse(g, dispersal_units_stock)

    return g,

def infect(g, dt, label="LeafElement"):
    """ Compute infection success by dispersal units.
    
    :Parameters:
      - `g` : MTG representing the canopy (and the soil). 'dispersal_units' are stored in the MTG as a property.
      - `dt` : time step of the simulation.
    
    :Example:
      >>> g = MTG()
      >>> stock = [SeptoriaDU(fungus = septoria(), nbSpores=random.randint(1,100), nature='emitted') for i in range(100)]
      >>> inoculator = RandomInoculation()
      >>> initiate(g, stock, inoculator)
      >>> dt = 1
      >>> nb_steps = 50
      >>> for i in range(nb_steps):
      >>>     update_climate(g)
      >>>     infect(g, dt)
      >>> return g
      
    """
    dispersal_units = g.property('dispersal_units')
    for vid, du in dispersal_units.iteritems():
        if g.label(vid).startswith(label):
            for dispersal_unit in du:
                leaf = g.node(vid)
                if dispersal_unit.active: # TODO : Condition here ?
                    dispersal_unit.infect(dt, leaf)

    return g,
    
def update(g, dt, label="LeafElement"):
    """ Update the status of every lesion on the MTG.
    
    :Parameters:
      - `g` : MTG representing the canopy (and the soil). 'lesions' are stored in the MTG as a property.
      - `dt` : time step of the simulation.
    
    :Example:
      >>> g = MTG()
      >>> stock = [SeptoriaDU(fungus = septoria(), nbSpores=random.randint(1,100), nature='emitted') for i in range(100)]
      >>> inoculator = RandomInoculation()
      >>> initiate(g, stock, inoculator)
      >>> dt = 1
      >>> nb_steps = 1000
      >>> for i in range(nb_steps):
      >>>     update_climate(g)
      >>>     infect(g, dt)
      >>>     update(g,dt)
      >>> return g
    
    """   
    lesions = g.property('lesions')
    for vid, l in lesions.iteritems():
        if g.label(vid).startswith(label):
            for lesion in l:
                # proposition 1 on fait ici une correspondance nom attendus dans g <-> noms caracterisant un environnement de lesion (classe a faire ??)
                leaf=g.node(vid)
                #proposition 2 : les conventions de nommage noms sont definies ailleurs (ou???) et on passe juste une leaf qui repond a cette convention
                lesion.update(dt, leaf)
          
    return g,
    
def disperse(g, 
             scene,
             dispersal_model,
             fungus_name, 
             label="LeafElement"):
    """ Disperse spores of the lesions of fungus identified by fungus_name.
    
    New infections occur only on nodes identified by label.
    
    :Parameters:
      - `g` : MTG representing the canopy (and the soil).
      - `dispersal_model` : model that allows positioning each DU in stock on g.
      - `lesion_factory` : class that generates a lesion of a given fungus.

    :Example:
      >>> 
    
    """
  
    # arrachage
    lesions = g.property('lesions')
    DU = {}
    for vid, l in lesions.iteritems():
        for lesion in l:
            if lesion.fungus.name is fungus_name:
                leaf = g.node(vid)
                if lesion.emissions:
                    if vid not in DU:
                        DU[vid] = []
                    DU[vid] += lesion.emissions # other derterminant (microclimate...) are expected on leaf
    
    # dispersion, position a sortir de du ??
    deposits = dispersal_model.disperse(scene, DU) # update DU in g , change position, nature
    # allocation of new dispersal units
    for vid,dlist in deposits.iteritems():
        if g.label(vid).startswith(label):
            leaf = g.node(vid)
            for d in dlist:
                d.deposited()
                if not 'dispersal_units' in leaf.properties():
                    leaf.dispersal_units=[]
                leaf.dispersal_units.append(d)

    return g,

def wash(g, washing_model, global_rain_intensity, label="LeafElement"): 
    """ Compute spores loss by washing.
    
    """
    washing_model.compute_washing_rate(g, global_rain_intensity) # compute washing rate on each leaf
    
    dispersal_units = g.property('dispersal_units')
    for vid, du in dispersal_units.iteritems():
        if g.label(vid).startswith(label):
            for dispersal_unit in du:
                leaf = g.node(vid)
                # inactive the DU according to the washing_rate on the leaf
                washing_model.wash(dispersal_unit, leaf.washing_rate)
    
    return g,

def growth_control(g, label="LeafElement"):
    """ Coordinate the growth of lesions according to the available space on the leaves.
    
    """
    vids = [v for v in g if g.label(v).startswith("LeafElement")]
    for v in vids:
        leaf = g.node(v)
        if 'lesions' in leaf.properties():
            lesions = leaf.lesions
            healthy_surface = leaf.healthy_surface
            # if n.parent() is None:#this is a new plant base
                # p = n.complex_at_scale(scale=1)
            total_demand = sum(l.growth_demand for l in lesions)
            
            if total_demand > healthy_surface:
                available_surface_by_lesion = healthy_surface / len(lesions)
                for l in lesions:
                    if available_surface_by_lesion < l.growth_demand:
                        l.growth_control(reduce_up_to = available_surface_by_lesion)                      
    
            # Update of 'healthy_surface' :
            total_lesions_surface = sum([l.surface for l in lesions])
            healthy_surface = max(0., leaf.surface - total_lesions_surface) 
            # FIXME : Should not need the 'max' operator ...
            leaf.healthy_surface = healthy_surface 
            # TODO : Right way to do this ???
            
    return g,

def nutrients_uptake(g):
    pass

    