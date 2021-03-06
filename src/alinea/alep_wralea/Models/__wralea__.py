
# This file has been generated at Fri Mar 15 18:44:25 2013

from openalea.core import *


__name__ = 'Alep.Models'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.8.0'
__authors__ = ''
__institutes__ = None
__icon__ = ''


__all__ = []

models_no_priority_growth_control = Factory(name='NoPriorityGrowthControl',
                                                         nodemodule='alinea.alep.growth_control',
                                                         nodeclass='NoPriorityGrowthControl',
                                               )
__all__.append('models_no_priority_growth_control')

models_random_dispersal = Factory(name='RandomDispersal',
                                               nodemodule='alinea.alep.dispersal_transport',
                                               nodeclass='RandomDispersal',
                                               )
__all__.append('models_random_dispersal')

models_random_inoculation = Factory(name='RandomInoculation',
                                               nodemodule='alinea.alep.inoculation',
                                               nodeclass='RandomInoculation',
                                               )
__all__.append('models_random_inoculation')