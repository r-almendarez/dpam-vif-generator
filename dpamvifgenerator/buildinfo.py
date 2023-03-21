######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
"""Build and version information"""
__version__ = "0.1.0"
__company__ = "VESA DPAM WG"
__product__ = "DPAM VIF Generator"
__bundle__ = (
    "{__company__}.{__product__}.({__version__})".format(**locals())
    .lower()
    .replace(" ", "-")
)
