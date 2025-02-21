# LinkML Issues

## Contextual Validation
If LinkML is to completely describe an RO-Crate profile, then it needs to be able to represent all aspects of that profile.
However, because LinkML models data in terms of classes and slots (properties), it doesn't capture some aspects of the RO-Crate specification that can't be modelled this way.

For example, consider the root dataset, ie
```json
{
    "@id": "./",
    "@type": "Dataset",
    ...
}
```


In LinkML, this is simply an instance of the `Dataset` class, since the `@type` is expected to uniquely define the class of the entity.
However, we need our root dataset to be treated differently.
Firstly, finding the root dataset is not trivial, and has to be defined in terms of [a series of rules](https://www.researchobject.org/ro-crate/specification/1.2-DRAFT/root-data-entity.html#finding-the-root-data-entity).
Then, once it's found, we need to apply [unique validation rules to it](https://www.researchobject.org/ro-crate/specification/1.2-DRAFT/root-data-entity.html#direct-properties-of-the-root-data-entity), such as mandating `datePublished`.
LinkML can't handle this sort of contextual validation which relies on information other than the object's fields to determine if it should apply.

In the context of profiles specifically, a crate that uses a profile must be expressed in this way:
```
{
    "@id": "./",
    "@type": "Dataset",
    "conformsTo":
        {"@id": "https://w3id.org/ro/wfrun/process/0.4"}       
}
```
Therefore, in our profile we will want to add a rule that says "the root data entity must have a `conformsTo` that points to the profile IRI".
However, we have the same issue here, because we can't identify the root data entity at all.

A lot of these same arguments can be made about the concept of ["Data Entities"](https://www.researchobject.org/ro-crate/specification/1.2-DRAFT/data-entities.html).
They can't be identified by `@type` alone, and the RO-Crate spec applies unique rules to them.

## Graph Rules

The purpose of this profile generation approach is to encode as much of the profile logic as possible in a machine readable form, so it can be used for validation or conformance testing.
So although it may not ever be possible to represent every part of a profile in a single format, the more it can represent the better.

Lets look at some of the purposes of an RO-Crate proifle, according to the RO-Crate 1.2 spec:

> The profile MAY require/suggest which @type of data entities and/or contextual entities are expected.

This can't be done with LinkML, since it's a statement about the graph itself: "the RO-Crate graph should contain one or more of these entities".
Despite having some linked data compatible features such as IRIs, LinkML can't make an assertion about the graph like this.

## Missing LinkML Features

Some aspects of RO-Crate could be eventually supported by LinkML, but there is currently no support in the tooling.

* It's essential that RO-Crate entities are not limited to a strict set of properties. Unfortunately LinkML doesn't yet support classes that allow "extra" properties. https://github.com/linkml/linkml/issues/2241
* Since RO-Crate is just a JSON serialization of RDF, `"someProperty": ["foo"]` and `"someProperty": "foo"` need to be treated equivalently. However, this isn't supported by the LinkML JSON loader. It would be theoretically possible to use the following, except [this isn't implemented either](https://github.com/linkml/linkml/issues/2459).
```yaml
        one_of:
            - multivalued: true
            - multivalued: false
```
* LinkML can't load an entire graph. It needs to load a tree from a single root node. This isn't compatible with RO-Crate. See: https://github.com/linkml/linkml/issues/2477.
* LinkML doesn't support hybrid classes. RO-Crate and JSON-LD naturally allow `"@type": ["Foo", "Bar"]`, but there's no way to load such data in LinkML: https://github.com/linkml/linkml/issues/2478.

If the above issues were being actively worked on, then these wouldn't be a large concern, but most of these issues have had no progress in the months since I created them.
