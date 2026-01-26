# MEx invenio

Invenio-based institutional repository and metadata platform.

[![cookiecutter](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/cookiecutter.yml/badge.svg)](https://github.com/robert-koch-institut/mex-template)
[![cve-scan](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/cve-scan.yml)
[![linting](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/linting.yml)
[![open-code](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/open-code.yml/badge.svg)](https://gitlab.opencode.de/robert-koch-institut/mex/mex-invenio)
[![testing](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/testing.yml/badge.svg)](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/testing.yml)

## Project

The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

RKI cooperated with D4L data4life gGmbH for a pilot phase where the vision of a
FAIR metadata catalog was explored and concepts and prototypes were developed.
The partnership has ended with the successful conclusion of the pilot phase.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Aktuelles/Publikationen/Forschungsdaten/MEx/metadata-exchange-plattform-mex-node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

**Contact** \
For more information, please feel free to email us at [mex@rki.de](mailto:mex@rki.de).

### Publisher

**Robert Koch-Institut** \
Nordufer 20 \
13353 Berlin \
Germany

## Package

Invenio is an open source project that was initially developed by CERN. The
`mex-invenio` repository is an implementation of an Invenio instance for the Robert Koch
Institute. It will serve as the point of entry for the entire MEx project.

## License

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## Development

### Installation

- install python3.11 on your system
- on unix, run `make install`
- on windows, run `.\mex.bat install`

### Linting and testing

- run all linters with `make lint` or `.\mex.bat lint`
- run all tests with `make test` (see tests/TESTS.md for details)
