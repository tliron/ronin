
from .contexts import current_context
from .utils.paths import join_path, base_path
import inspect, sys

def configure_build(root_path=None, output_path_relative='build', binary_path_relative='bin', object_path_relative='obj', frame=1):
    with current_context(False) as ctx:
        if root_path is None:
            root_path = base_path(inspect.getfile(sys._getframe(frame)))
        ctx.input_path = root_path
        ctx.output_path = join_path(root_path, output_path_relative)
        ctx.binary_path_relative = binary_path_relative
        ctx.object_path_relative = object_path_relative
