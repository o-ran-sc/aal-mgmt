from cyborg.accelerator.drivers.co_processor.intel.driver import INTEL_Co_processorDriver
import os
import glob

from oslo_log import log as logging


__import__('pkg_resources').declare_namespace(__name__)
__import__(".".join([__package__, 'base']))


LOG = logging.getLogger(__name__)


def load_co_processor_vendor_driver():
    files = glob.glob(os.path.join(os.path.dirname(__file__), "*/driver*"))
    modules = set(map(lambda s: ".".join(s.rsplit(".")[0].rsplit("/", 2)[-2:]),
                      files))
    for m in modules:
        try:
            __import__(".".join([__package__, m]))
            LOG.debug("Successfully loaded Co-processor vendor driver: %s." % m)
        except ImportError as e:
            LOG.error("Failed to load Co-processor vendor driver: %s. Details: %s"
                      % (m, e))


load_co_processor_vendor_driver()
