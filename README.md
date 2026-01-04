# PSEC - Platform Security Enforced Core

This project provides a software architecture for creating security products.

> ⚠️ **Important Notice**

This repository is subject to a restrictive license.  
You are **not allowed to fork, copy, modify, or reuse** this code in any form, including through GitHub features, **without explicit written permission** from the author.

## Documentation

Newcomers should begin with the [architecture documentation](python/lib/docs/source/markdown/architecture.md).

API is documented in the [protocol documentation](python/lib/docs/source/markdown/protocol.md) for the Messages and in the [API documentation (HTML)](python/lib/docs/build/html/psec.html#psec.Api) for the *python API*.

All python classes documentation (*docstrings*) is provided as HTML pages in the folder `python/lib/docs/build/html`.

## Project directory structure

The project is divided into different parts :

| Folder | Description|
|--|--|
| certs | contains the public key for the Alpine repository |
| misc | contains different objects like fonts, logos and scripts |
| python | contains the source code of the projet [See README.md](python/README.md) |
| setup | contains the source code of the Alpine packages [See README.md](setup/README.md) |

## Licence

Please read the [licence](python/lib/LICENCE.md) carefully before using this product. 

## Releases

*Please notice that only x86_64 packages are available*

The releases are available in the [official repository](https://alefbet.net/repositories/PSEC).

Add the following in `/etc/apk/repositories`:
```
https://alefbet.net/repositories/PSEC
```

The [public key file](https://alefbet.net/repositories/PGP/psec.rsa.pub) must be downloaded into `/etc/apk/keys`.

## First use

When you use PSEC for the first time we suggest you start with the [demonstration app](python/demo/README.md) or the [diagnostic app](python/diag/README.md).

Follow the instruction in the [provisioning](python/lib/docs/source/markdown/provisioning.md) documentation.

**Please notice that your hardware must be compatible with VT-d and VT-x. This can be verified with the [diagnostic app](python/diag/README.md).**