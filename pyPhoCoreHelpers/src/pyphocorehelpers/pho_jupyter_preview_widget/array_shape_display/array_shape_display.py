import math
from jinja2 import Template

def to_svg(chunks, size=120):
    """Convert chunks into an SVG grid."""
    # Simplified SVG generation logic
    svg = f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">'
    total_size = sum(sum(dim) for dim in chunks)
    scale = size / total_size
    y_offset = 0
    for dim in chunks:
        x_offset = 0
        for block in dim:
            width = block * scale
            height = block * scale
            svg += f'<rect x="{x_offset}" y="{y_offset}" width="{width}" height="{height}" fill="blue" stroke="black"/>'
            x_offset += width
        y_offset += height
    svg += "</svg>"
    return svg

def format_bytes(nbytes):
    """Format bytes as human-readable."""
    if nbytes < 1024:
        return f"{nbytes} B"
    elif nbytes < 1024**2:
        return f"{nbytes / 1024:.1f} KB"
    elif nbytes < 1024**3:
        return f"{nbytes / 1024**2:.1f} MB"
    else:
        return f"{nbytes / 1024**3:.1f} GB"

def maybe_pluralize(count, noun):
    """Return pluralized noun if count > 1."""
    return f"{count} {noun}" + ("s" if count > 1 else "")

def array_repr_html(shape, chunks, dtype, size=120):
    """Generate an HTML representation of an array's shape and chunks."""
    # Handle case when chunks is None (standard NumPy arrays)
    if chunks is None:
        # For NumPy arrays, create a simple representation with just one chunk per dimension
        chunks = [[dim] for dim in shape]

    svg = to_svg(chunks, size=size)
    nbytes = math.prod(shape) * dtype.itemsize if dtype and shape else "unknown"
    cbytes = math.prod(max(dim) for dim in chunks) * dtype.itemsize if dtype else "unknown"

    template = Template("""
    <div>
        <div>{{ grid }}</div>
        <p>Shape: {{ array.shape }}</p>
        <p>Chunk size: {{ array.chunksize }}</p>
        <p>Total size: {{ nbytes }}</p>
        <p>Chunk memory: {{ cbytes }}</p>
        <p>{{ layers }}</p>
    </div>
    """)
    
    layers = maybe_pluralize(len(chunks), "graph layer")

    return template.render(
        # array={"shape": shape, "chunksize": max(dim) for dim in chunks},
        array={"shape": shape, "chunksize": [max(dim) for dim in chunks]},
        grid=svg,
        nbytes=format_bytes(nbytes) if nbytes != "unknown" else "unknown",
        cbytes=format_bytes(cbytes) if cbytes != "unknown" else "unknown",
        layers=layers,
    )


""" 

import pyphocorehelpers.pho_jupyter_preview_widget as pho_jupyter_preview_widget


from pyphocorehelpers.pho_jupyter_preview_widget.array_shape_display import array_repr_html
from pyphocorehelpers.pho_jupyter_preview_widget.array_shape_display.array_shape_display import array_repr_html


from pyphocorehelpers.pho_jupyter_preview_widget.array_shape_display.array_shape_display import array_repr_html


array_repr_html

"""