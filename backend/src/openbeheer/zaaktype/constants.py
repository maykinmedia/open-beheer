from openbeheer.types.ztc import ZaakType
from openbeheer.types._open_beheer import DataGroup
from django.utils.translation import gettext_lazy as __

ZAAKTYPE_DATA_GROUPS = {
    "overview": DataGroup(
        label=__("Overview"),
        fields=[
            ZaakType.identificatie.__name__,
            ZaakType.omschrijving.__name__,
            ZaakType.doel.__name__,
            ZaakType.selectielijst_procestype.__name__,
        ],
    ),
    "general": DataGroup(
        label=__("General details"),
        fields=[
            DataGroup(
                label=__("Content & Process"),
                fields=[
                    ZaakType.doel.__name__,
                    ZaakType.onderwerp.__name__,
                    ZaakType.aanleiding.__name__,
                    DataGroup(
                        label=__("Process flow"),
                        fields=[
                            ZaakType.handeling_initiator.__name__,
                            ZaakType.handeling_behandelaar.__name__,
                            ZaakType.verantwoordelijke.__name__,
                            ZaakType.producten_of_diensten.__name__,
                            ZaakType.doorlooptijd.__name__,
                            ZaakType.servicenorm.__name__,
                        ],
                    ),
                ],
            ),
            DataGroup(
                label=__("Publication & Visibility"),
                fields=[
                    ZaakType.omschrijving.__name__,
                    ZaakType.omschrijving_generiek.__name__,
                    ZaakType.indicatie_intern_of_extern.__name__,
                    ZaakType.vertrouwelijkheidaanduiding.__name__,
                    DataGroup(
                        label=__("Publication"),
                        fields=[
                            ZaakType.publicatie_indicatie.__name__,
                            ZaakType.publicatietekst.__name__,
                        ],
                    ),
                ],
            ),
            DataGroup(
                label=__("Administration & Archiving"),
                fields=[
                    DataGroup(
                        label=__("Municipality selectielijst"),
                        fields=[
                            ZaakType.selectielijst_procestype.__name__,
                            # TODO: fields about selectielijst_procestype that need to be expanded.
                        ],
                    ),
                    DataGroup(
                        label=__("Reference process"),
                        fields=[
                            ZaakType.referentieproces.__name__,
                            # TODO: expand fields of the referentie process,
                        ],
                    ),
                ],
            ),
            DataGroup(
                label=__("Structure & Connections"),
                fields=[
                    DataGroup(
                        label=__("Zaaktypecode"),
                        fields=[
                            ZaakType.identificatie.__name__,
                            # TODO: Zaaktype UUID
                        ],
                    ),
                    DataGroup(
                        label=__("Gerelateerde zaaktypen"),
                        fields=[
                            ZaakType.gerelateerde_zaaktypen.__name__,
                            # TODO: expand with some sort of label
                        ],
                    ),
                    DataGroup(
                        label=__("Source details"),
                        fields=[
                            ZaakType.broncatalogus.__name__,
                            # TODO: expand catalogus
                        ],
                    ),
                ],
            ),
            DataGroup(
                label=__("Validity & Explanation"),
                fields=[
                    # TODO: design in progress
                ],
            ),
        ],
    ),
}
