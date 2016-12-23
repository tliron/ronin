
from .utils import build_path

def configure_build(ctx, base_path, output_path_relative='build', binary_path_relative='bin', debug=True):
    ctx.input_path = base_path
    ctx.output_path = build_path(base_path, output_path_relative)
    ctx.binary_path_relative = binary_path_relative
    ctx.debug = debug
