

# PROCLaim (Profiles in RO-Crate from LinkML)

Generate spec-conformant RO-Crate profile crates from a user friendly
LinkML schema.

Running PROCLaim on a LinkML schema gives you a [Profile
Crate](https://www.researchobject.org/ro-crate/specification/1.2-DRAFT/profiles.html#profile-crate)
containing:

- Human readable HTML documentation for your profile
- Human-readable vocabulary pages for your custom types and properties
- `ro-crate-metadata.json` that describes the profile
- SHACL shapes for validating against your profile
- Mode file compatible with the [Crate-O
  GUI](https://github.com/Language-Research-Technology/crate-o)
- A copy of the original LinkML schema

## Motivation

The upcoming RO-Crate 1.2 release adds support for
[profiles](https://www.researchobject.org/ro-crate/specification/1.2-DRAFT/profiles.html),
which allow you to define an extension of the RO-Crate specification,
with new types, properties and validations. However, there are several
steps you have to follow to follow best practices. You need to:

- Create an HTML document describing your profile to humans
- Create an `ro-crate-metadata.json` that describes your profile in RDF
- Define validations for your profile using SHACL or some other
  validation system
- Write integrations with tools such as the Crate-O GUI
- Create a resolvable URL for each of your new properties and types

Not only does this require learning several different specifications,
but it’s also different to keep all of this in sync when you want to
make a change. PROCLaim solves this by making a single LinkML schema the
source of truth for your profile. LinkML is written in YAML, and has
excellent documentation and tooling that you can rely on to build your
schema.

## Installation

``` bash
pip install git+https://github.com/WEHI-SODA-Hub/proclaim.git
```

## Usage

PROClaim is a Python library, but the main way you interact with it is
via the `proclaim-profile` command-line tool. For example, assuming we
already have [a complete LinkML
schema](https://github.com/WEHI-SODA-Hub/proclaim/blob/main/test/process_run.yaml)
describing the [Process Run
Profile](https://www.researchobject.org/workflow-run-crate/profiles/process_run_crate/),
we could do the following:

``` bash
proclaim-profile test/process_run.yaml --output-dir process_run_profile/
```

    WARNING:linkml.utils.generator:File "process_run.yaml", line 21, col 15: Unrecognized prefix: wfrun
    WARNING:linkml.utils.generator:File "process_run.yaml", line 21, col 15: Unrecognized prefix: wfrun
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#implements
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#changes
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#consolidates
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#date_document
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#version_date
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#id_local
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#jurisdiction
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#in_force
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#legal_value
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#passed_by
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#responsibility_of
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#transposes
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#type_document
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#InForce
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#LegalValue
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#LegalExpression
    WARNING:linkml.utils.generator:No namespace defined for URI: http://data.europa.eu/eli/ontology#Format
    WARNING:linkml.utils.generator:No namespace defined for URI: http://www.w3.org/ns/regorg#RegisteredOrganization

``` bash
tree process_run_profile/
```

    process_run_profile/
    ├── 404.html
    ├── classes
    │   ├── ContainerImage
    │   │   └── index.html
    │   ├── DockerImage
    │   │   └── index.html
    │   ├── ParameterConnection
    │   │   └── index.html
    │   └── SIFImage
    │       └── index.html
    ├── css
    │   ├── base.css
    │   ├── bootstrap.min.css
    │   ├── bootstrap.min.css.map
    │   ├── brands.min.css
    │   ├── fontawesome.min.css
    │   ├── solid.min.css
    │   └── v4-font-face.min.css
    ├── img
    │   ├── favicon.ico
    │   └── grid.png
    ├── index.html
    ├── js
    │   ├── base.js
    │   ├── bootstrap.bundle.min.js
    │   ├── bootstrap.bundle.min.js.map
    │   └── darkmode.js
    ├── linkml.yml
    ├── mode.json
    ├── properties
    │   ├── connection
    │   │   └── index.html
    │   ├── containerImage
    │   │   └── index.html
    │   ├── environment
    │   │   └── index.html
    │   ├── md5
    │   │   └── index.html
    │   ├── registry
    │   │   └── index.html
    │   ├── resourceUsage
    │   │   └── index.html
    │   ├── sha1
    │   │   └── index.html
    │   ├── sha256
    │   │   └── index.html
    │   ├── sha512
    │   │   └── index.html
    │   ├── sourceParameter
    │   │   └── index.html
    │   ├── tag
    │   │   └── index.html
    │   └── targetParameter
    │       └── index.html
    ├── ro-crate-metadata.json
    ├── search
    │   ├── lunr.js
    │   ├── main.js
    │   ├── search_index.json
    │   └── worker.js
    ├── shapes.ttl
    ├── sitemap.xml
    ├── sitemap.xml.gz
    └── webfonts
        ├── fa-brands-400.ttf
        ├── fa-brands-400.woff2
        ├── fa-regular-400.ttf
        ├── fa-regular-400.woff2
        ├── fa-solid-900.ttf
        ├── fa-solid-900.woff2
        ├── fa-v4compatibility.ttf
        └── fa-v4compatibility.woff2

    24 directories, 49 files
