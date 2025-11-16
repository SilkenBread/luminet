STATUS = (
    (1, 'Malo'),
    (2, 'Bueno'),
    (3, 'Regular'),
)

USING = (
    (1, 'Compartido distribución'),
    (2, 'Exclusivo AP')
)

# TRANSFORMADOR
TRAFO_TYPE = (
    (1, 'Monofásico'),
    (2, 'Trifásico'),
)
TRAFO_PROPERTY = (
    (1, 'EMCALI'),
    (2, 'Exclusivo'),
    (3, 'Tercero o privado'),
)
TRAFO_INSTALLATION = (
    ('OH', 'Poste'),
    ('SU', 'Superficie'),
    ('UG', 'Subterráneo (Subestación)')
)

# CAJA AP
APBOX_TYPE = (
    (1, 'Alumbrado Público'),
    (2, 'Baja tensión'),
)
APBOX_PROPERTY = (
    (1, 'Alumbrado Público'),
    (2, 'Distribución Emcali'),
)

# RED
NET_INSTALLATION = (
    (1, 'Aérea'),
    (2, 'Subterránea'),
)
NET_CONDUCTOR = (
    (1, 'Aislado'),
    (2, 'Desnudo'),
    (3, 'Mixto'),
)

NET_SETTING = (
    (1, 'Abierta'),
    (2, 'trenzada'),
    (3, 'Ducto'),
)
NET_SURFACE = (
    (1, 'Concreto (Zona Duras)'),
    (2, 'Tierra-Suelo (Zona blanda)'),
)

# POSTE
SUPPORT_STATUS = (
    (1, 'Malo'),
    (2, 'Bueno'),
    (3, 'Regular'),
    (4, 'Agrietado'),
    (5, 'Oxidado'),
    (6, 'Golpeado'),
)
SUPPORT_PROPERTY = (
    (1, 'Exclusivo Alumbrado Público'),
    (2, 'Distribución'),
    (3, 'Particular'),
    (4, 'Otro'),
)


TYPE_AREA = (
    (1, 'Municipal'),
    (2, 'Rural'),
)