__version__ = '0.1'

from .config import logger
from .cac.Application import Application
from .front.Facade import FacadeWsService
from .front.Client import Client
from .trafficReporter.Reporter import TrafficReporter

# Setup application
def run():
  frontClient = Client()
  TrafficReporter(frontClient)
  Cac = Application(frontClient)
  Cac.run()

  if Cac.listen:
    FacadeApp = FacadeWsService()
    FacadeApp.register_command(Cac.toggleCac, 'toggleCac')
    FacadeApp.register_command(Cac.toggleQos, 'toggleQos')
    FacadeApp.register_command(Cac.getTopologyLinks, 'getTopologyLinks')
    FacadeApp.register_command(Cac.getTopologySwitches, 'getTopologySwitches')
    FacadeApp.run(frontClient)
