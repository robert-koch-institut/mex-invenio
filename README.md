# MEx invenio

Invenio-based institutional repository and metadata platform.

[![cve-scan](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/cve-scan.yml)
[![linting](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-invenio/actions/workflows/linting.yml)

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

## License

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## Development

### Installation

- on unix, consider using pyenv https://github.com/pyenv/pyenv
  - get pyenv `curl https://pyenv.run | bash`
  - install 3.9 `pyenv install 3.9`
  - switch version `pyenv global 3.9`
  - run `make install`
- on windows, consider using pyenv-win https://pyenv-win.github.io/pyenv-win/
  - follow https://pyenv-win.github.io/pyenv-win/#quick-start
  - install 3.9 `pyenv install 3.9`
  - switch version `pyenv global 3.9`
  - run `.\mex.bat install`

### Linting

- run all linters with `pre-commit run --all-files`

### Unit testing

Unit testing is done using a customised version of pytest, [pytest-invenio](https://github.com/inveniosoftware/pytest-invenio).
Tests are stored in `./tests`.

To install the testing environment, run the following command:

```bash
pipenv install -d
```

To run the tests, execute the following command:

```bash
./run-tests.sh
```
