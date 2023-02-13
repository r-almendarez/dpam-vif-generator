"""Build and version information"""
__version__ = "0.1.0"
__company__ = "VESA DPAM WG"
__product__ = "DPAM VIF Generator"
__bundle__ = (
    "{__company__}.{__product__}.({__version__})".format(**locals())
    .lower()
    .replace(" ", "-")
)
