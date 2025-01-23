from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'http://example.org/RoCrateProfile/',
     'id': 'http://example.org/RoCrateProfile',
     'name': 'RoCrateProfile',
     'types': {'Text': {'base': 'str',
                        'from_schema': 'http://example.org/RoCrateProfile',
                        'name': 'Text',
                        'typeof': 'string',
                        'uri': 'https://schema.org/Number'},
               'URL': {'base': 'str',
                       'from_schema': 'http://example.org/RoCrateProfile',
                       'name': 'URL',
                       'repr': 'str',
                       'typeof': 'uri',
                       'uri': 'https://schema.org/URL'}}} )


class DefinedTerm(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:DefinedTerm',
         'comments': ['A word, name, acronym, phrase, etc. with a formal definition. '
                      'Often used in the context of category or subject '
                      'classification, glossaries or dictionaries, product or creative '
                      'work types, etc. Use the name property for the term being '
                      'defined, use termCode if the term has an alpha-numeric code '
                      'allocated, use description to provide the definition of the '
                      'term.'],
         'from_schema': 'http://example.org/RoCrateProfile'})

    termCode: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'termCode',
         'comments': ['A code that identifies this [[DefinedTerm]] within a '
                      '[[DefinedTermSet]].'],
         'domain_of': ['DefinedTerm'],
         'slot_uri': 'schema:termCode'} })


class Thing(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Thing',
         'comments': ['The most generic type of item.'],
         'from_schema': 'http://example.org/RoCrateProfile'})

    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


class CreativeWork(Thing):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:CreativeWork',
         'comments': ['The most generic kind of creative work, including books, '
                      'movies, photographs, software programs, etc.'],
         'from_schema': 'http://example.org/RoCrateProfile'})

    encodingFormat: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'encodingFormat',
         'comments': ['Media type typically expressed using a MIME format (see [IANA '
                      'site](http://www.iana.org/assignments/media-types/media-types.xhtml) '
                      'and [MDN '
                      'reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)), '
                      'e.g. application/zip for a SoftwareApplication binary, '
                      'audio/mpeg for .mp3 etc.\n'
                      '\n'
                      'In cases where a [[CreativeWork]] has several media type '
                      'representations, [[encoding]] can be used to indicate each '
                      '[[MediaObject]] alongside particular [[encodingFormat]] '
                      'information.\n'
                      '\n'
                      'Unregistered or niche encoding and file formats can be '
                      'indicated instead via the most appropriate URL, e.g. defining '
                      'Web page or a Wikipedia/Wikidata entry.'],
         'domain_of': ['CreativeWork', 'MediaObject', 'File'],
         'slot_uri': 'schema:encodingFormat'} })
    version: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'version',
         'comments': ['The version of the CreativeWork embodied by a specified '
                      'resource.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:version'} })
    about: Optional[Thing] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'about',
         'comments': ['The subject matter of the content.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:about'} })
    hasPart: Optional[CreativeWork] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'comments': ['Indicates an item or CreativeWork that is part of this item, or '
                      'CreativeWork (in some sense).'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:hasPart'} })
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


class Dataset(CreativeWork):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Dataset',
         'comments': ['A body of structured information describing some topic(s) of '
                      'interest.'],
         'from_schema': 'http://example.org/RoCrateProfile'})

    distribution: Optional[DataDownload] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'distribution',
         'comments': ['A downloadable form of this dataset, at a specific location, in '
                      'a specific format. This property can be repeated if different '
                      'variations are available. There is no expectation that '
                      'different downloadable distributions must contain exactly '
                      'equivalent information (see also '
                      '[DCAT](https://www.w3.org/TR/vocab-dcat-3/#Class:Distribution) '
                      'on this point). Different distributions might include or '
                      'exclude different subsets of the entire dataset, for example.'],
         'domain_of': ['Dataset'],
         'slot_uri': 'schema:distribution'} })
    encodingFormat: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'encodingFormat',
         'comments': ['Media type typically expressed using a MIME format (see [IANA '
                      'site](http://www.iana.org/assignments/media-types/media-types.xhtml) '
                      'and [MDN '
                      'reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)), '
                      'e.g. application/zip for a SoftwareApplication binary, '
                      'audio/mpeg for .mp3 etc.\n'
                      '\n'
                      'In cases where a [[CreativeWork]] has several media type '
                      'representations, [[encoding]] can be used to indicate each '
                      '[[MediaObject]] alongside particular [[encodingFormat]] '
                      'information.\n'
                      '\n'
                      'Unregistered or niche encoding and file formats can be '
                      'indicated instead via the most appropriate URL, e.g. defining '
                      'Web page or a Wikipedia/Wikidata entry.'],
         'domain_of': ['CreativeWork', 'MediaObject', 'File'],
         'slot_uri': 'schema:encodingFormat'} })
    version: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'version',
         'comments': ['The version of the CreativeWork embodied by a specified '
                      'resource.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:version'} })
    about: Optional[Thing] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'about',
         'comments': ['The subject matter of the content.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:about'} })
    hasPart: Optional[CreativeWork] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'comments': ['Indicates an item or CreativeWork that is part of this item, or '
                      'CreativeWork (in some sense).'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:hasPart'} })
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


class MediaObject(CreativeWork):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:MediaObject',
         'comments': ['A media object, such as an image, video, audio, or text object '
                      'embedded in a web page or a downloadable dataset i.e. '
                      'DataDownload. Note that a creative work may have many media '
                      'objects associated with it on the same web page. For example, a '
                      'page about a single song (MusicRecording) may have a music '
                      'video (VideoObject), and a high and low bandwidth audio stream '
                      "(2 AudioObject's)."],
         'from_schema': 'http://example.org/RoCrateProfile'})

    encodingFormat: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'encodingFormat',
         'comments': ['Media type typically expressed using a MIME format (see [IANA '
                      'site](http://www.iana.org/assignments/media-types/media-types.xhtml) '
                      'and [MDN '
                      'reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)), '
                      'e.g. application/zip for a SoftwareApplication binary, '
                      'audio/mpeg for .mp3 etc.\n'
                      '\n'
                      'In cases where a [[CreativeWork]] has several media type '
                      'representations, [[encoding]] can be used to indicate each '
                      '[[MediaObject]] alongside particular [[encodingFormat]] '
                      'information.\n'
                      '\n'
                      'Unregistered or niche encoding and file formats can be '
                      'indicated instead via the most appropriate URL, e.g. defining '
                      'Web page or a Wikipedia/Wikidata entry.'],
         'domain_of': ['CreativeWork', 'MediaObject', 'File'],
         'slot_uri': 'schema:encodingFormat'} })
    version: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'version',
         'comments': ['The version of the CreativeWork embodied by a specified '
                      'resource.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:version'} })
    about: Optional[Thing] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'about',
         'comments': ['The subject matter of the content.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:about'} })
    hasPart: Optional[CreativeWork] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'comments': ['Indicates an item or CreativeWork that is part of this item, or '
                      'CreativeWork (in some sense).'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:hasPart'} })
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


class DataDownload(MediaObject):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:DataDownload',
         'comments': ['All or part of a [[Dataset]] in downloadable form. '],
         'from_schema': 'http://example.org/RoCrateProfile'})

    encodingFormat: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'encodingFormat',
         'comments': ['Media type typically expressed using a MIME format (see [IANA '
                      'site](http://www.iana.org/assignments/media-types/media-types.xhtml) '
                      'and [MDN '
                      'reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)), '
                      'e.g. application/zip for a SoftwareApplication binary, '
                      'audio/mpeg for .mp3 etc.\n'
                      '\n'
                      'In cases where a [[CreativeWork]] has several media type '
                      'representations, [[encoding]] can be used to indicate each '
                      '[[MediaObject]] alongside particular [[encodingFormat]] '
                      'information.\n'
                      '\n'
                      'Unregistered or niche encoding and file formats can be '
                      'indicated instead via the most appropriate URL, e.g. defining '
                      'Web page or a Wikipedia/Wikidata entry.'],
         'domain_of': ['CreativeWork', 'MediaObject', 'File'],
         'slot_uri': 'schema:encodingFormat'} })
    version: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'version',
         'comments': ['The version of the CreativeWork embodied by a specified '
                      'resource.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:version'} })
    about: Optional[Thing] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'about',
         'comments': ['The subject matter of the content.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:about'} })
    hasPart: Optional[CreativeWork] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'comments': ['Indicates an item or CreativeWork that is part of this item, or '
                      'CreativeWork (in some sense).'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:hasPart'} })
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


class SoftwareApplication(CreativeWork):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:SoftwareApplication',
         'comments': ['A software application.'],
         'from_schema': 'http://example.org/RoCrateProfile'})

    encodingFormat: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'encodingFormat',
         'comments': ['Media type typically expressed using a MIME format (see [IANA '
                      'site](http://www.iana.org/assignments/media-types/media-types.xhtml) '
                      'and [MDN '
                      'reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)), '
                      'e.g. application/zip for a SoftwareApplication binary, '
                      'audio/mpeg for .mp3 etc.\n'
                      '\n'
                      'In cases where a [[CreativeWork]] has several media type '
                      'representations, [[encoding]] can be used to indicate each '
                      '[[MediaObject]] alongside particular [[encodingFormat]] '
                      'information.\n'
                      '\n'
                      'Unregistered or niche encoding and file formats can be '
                      'indicated instead via the most appropriate URL, e.g. defining '
                      'Web page or a Wikipedia/Wikidata entry.'],
         'domain_of': ['CreativeWork', 'MediaObject', 'File'],
         'slot_uri': 'schema:encodingFormat'} })
    version: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'version',
         'comments': ['The version of the CreativeWork embodied by a specified '
                      'resource.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:version'} })
    about: Optional[Thing] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'about',
         'comments': ['The subject matter of the content.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:about'} })
    hasPart: Optional[CreativeWork] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'comments': ['Indicates an item or CreativeWork that is part of this item, or '
                      'CreativeWork (in some sense).'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:hasPart'} })
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


class DefinedTermSet(CreativeWork):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:DefinedTermSet',
         'comments': ['A set of defined terms, for example a set of categories or a '
                      'classification scheme, a glossary, dictionary or enumeration.'],
         'from_schema': 'http://example.org/RoCrateProfile'})

    encodingFormat: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'encodingFormat',
         'comments': ['Media type typically expressed using a MIME format (see [IANA '
                      'site](http://www.iana.org/assignments/media-types/media-types.xhtml) '
                      'and [MDN '
                      'reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)), '
                      'e.g. application/zip for a SoftwareApplication binary, '
                      'audio/mpeg for .mp3 etc.\n'
                      '\n'
                      'In cases where a [[CreativeWork]] has several media type '
                      'representations, [[encoding]] can be used to indicate each '
                      '[[MediaObject]] alongside particular [[encodingFormat]] '
                      'information.\n'
                      '\n'
                      'Unregistered or niche encoding and file formats can be '
                      'indicated instead via the most appropriate URL, e.g. defining '
                      'Web page or a Wikipedia/Wikidata entry.'],
         'domain_of': ['CreativeWork', 'MediaObject', 'File'],
         'slot_uri': 'schema:encodingFormat'} })
    version: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'version',
         'comments': ['The version of the CreativeWork embodied by a specified '
                      'resource.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:version'} })
    about: Optional[Thing] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'about',
         'comments': ['The subject matter of the content.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:about'} })
    hasPart: Optional[CreativeWork] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'comments': ['Indicates an item or CreativeWork that is part of this item, or '
                      'CreativeWork (in some sense).'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:hasPart'} })
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


class ResourceDescriptor(ConfiguredBaseModel):
    """
    A description of a resource that defines an aspect - a particular part, feature or role - of a Profile
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': ':ResourceDescriptor',
         'from_schema': 'http://example.org/RoCrateProfile'})

    hasArtifact: Optional[str] = Field(None, description="""The URL of a downloadable file with particulars such as its format and role indicated by the Resource Descriptor""", json_schema_extra = { "linkml_meta": {'alias': 'hasArtifact',
         'domain_of': ['ResourceDescriptor'],
         'slot_uri': ':hasArtifact'} })
    hasRole: Optional[Concept] = Field(None, description="""The function of an artifact described by a Resource Descriptor, such as specification, guidance etc.""", json_schema_extra = { "linkml_meta": {'alias': 'hasRole',
         'domain_of': ['ResourceDescriptor'],
         'slot_uri': ':hasRole'} })


class Standard(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'dct:Standard',
         'from_schema': 'http://example.org/RoCrateProfile'})

    pass


class Profile(Standard):
    """
    A specification that constrains, extends, combines, or provides guidance or explanation about the usage of other specifications.

    This definition includes what are often called \"application profiles\", \"metadata application profiles\", or \"metadata profiles\".
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': ':Profile',
         'from_schema': 'http://example.org/RoCrateProfile',
         'source': 'https://www.w3.org/2017/dxwg/wiki/ProfileContext'})

    isProfileOf: Optional[Standard] = Field(None, description="""A specification for which this Profile defines constraints, extensions, or which it uses in combination with other specifications, or provides guidance or explanation about its usage""", json_schema_extra = { "linkml_meta": {'alias': 'isProfileOf',
         'domain_of': ['Profile'],
         'slot_uri': ':isProfileOf',
         'subproperty_of': 'isTransitiveProfileOf'} })


class Concept(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'skos:Concept',
         'from_schema': 'http://example.org/RoCrateProfile'})

    pass


class ResourceRole(Concept):
    """
    A role that an profile resource, described by a Resource Descriptor, plays
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': ':ResourceRole',
         'from_schema': 'http://example.org/RoCrateProfile'})

    pass


class Collection(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'pcdm:Collection',
         'comments': ['\n'
                      '        A Collection is a group of resources. Collections have '
                      'descriptive metadata, access metadata,\n'
                      '        and may links to works and/or collections. By default, '
                      'member works and collections are an\n'
                      '        unordered set, but can be ordered using the ORE Proxy '
                      'class.\n'
                      '      '],
         'from_schema': 'http://example.org/RoCrateProfile'})

    pass


class File(CreativeWork):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:MediaObject',
         'comments': ['A media object, such as an image, video, audio, or text object '
                      'embedded in a web page or a downloadable dataset i.e. '
                      'DataDownload. Note that a creative work may have many media '
                      'objects associated with it on the same web page. For example, a '
                      'page about a single song (MusicRecording) may have a music '
                      'video (VideoObject), and a high and low bandwidth audio stream '
                      "(2 AudioObject's)."],
         'from_schema': 'http://example.org/RoCrateProfile'})

    encodingFormat: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'encodingFormat',
         'comments': ['Media type typically expressed using a MIME format (see [IANA '
                      'site](http://www.iana.org/assignments/media-types/media-types.xhtml) '
                      'and [MDN '
                      'reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)), '
                      'e.g. application/zip for a SoftwareApplication binary, '
                      'audio/mpeg for .mp3 etc.\n'
                      '\n'
                      'In cases where a [[CreativeWork]] has several media type '
                      'representations, [[encoding]] can be used to indicate each '
                      '[[MediaObject]] alongside particular [[encodingFormat]] '
                      'information.\n'
                      '\n'
                      'Unregistered or niche encoding and file formats can be '
                      'indicated instead via the most appropriate URL, e.g. defining '
                      'Web page or a Wikipedia/Wikidata entry.'],
         'domain_of': ['CreativeWork', 'MediaObject', 'File'],
         'slot_uri': 'schema:encodingFormat'} })
    version: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'version',
         'comments': ['The version of the CreativeWork embodied by a specified '
                      'resource.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:version'} })
    about: Optional[Thing] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'about',
         'comments': ['The subject matter of the content.'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:about'} })
    hasPart: Optional[CreativeWork] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'comments': ['Indicates an item or CreativeWork that is part of this item, or '
                      'CreativeWork (in some sense).'],
         'domain_of': ['CreativeWork'],
         'slot_uri': 'schema:hasPart'} })
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:name'} })
    url: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'url',
         'comments': ['URL of the item.'],
         'domain_of': ['Thing'],
         'slot_uri': 'schema:url'} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
DefinedTerm.model_rebuild()
Thing.model_rebuild()
CreativeWork.model_rebuild()
Dataset.model_rebuild()
MediaObject.model_rebuild()
DataDownload.model_rebuild()
SoftwareApplication.model_rebuild()
DefinedTermSet.model_rebuild()
ResourceDescriptor.model_rebuild()
Standard.model_rebuild()
Profile.model_rebuild()
Concept.model_rebuild()
ResourceRole.model_rebuild()
Collection.model_rebuild()
File.model_rebuild()
