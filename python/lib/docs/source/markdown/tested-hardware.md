# Tested hardware

This document describes tested hardware configurations.

## Synthesis

| Type | Manufacturer | Model | CPU | GPU | Virt. | IOMMU | Compatibility |
|--|--|--|--|--|--|
| Tablet | Durabook | R8 | Intel Core i5 1230U | | Yes | Yes | 100% (1) |
| Laptop | Dell | Latitude E5510 | | | Yes | Yes | |

(1) specific configuration is needed.

## Durabook R8

This tablet is know to work with the exclusion of the PCI bus `00:0d.0` which causes an hangout during the boot.

# Dell Latitude E5510