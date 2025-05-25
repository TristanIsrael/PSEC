# PSEC Diag

PSEC Diagnostic tool is a simple way of veryfing that a platform can run a product based on PSEC and evaluate the level of security offered.

You can create an USB disk and use it on multiple platforms to verify their capacity.

> ⚠️ **Notice**
>
> The platform virtualization and security capabilities depend on the settings of the BIOS or EFI. Please adapt the settings to enable VT-d/AMD-Vi (or IOMMU) and VT-x/AMD-V.

## Screenshot

![Screenshot of PSEC Diag](docs/images/screenshot.png)

## Create an USB disk

Download the image file of [psec-diag](https://www.alefbet.net/images/psec-diag.img) and recreate the USB disk using `dd`, or `Rufus` for example.