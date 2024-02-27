VALID_TAG_CHARS = '0289PYLQGRJCUV'


def normalize_tag(tag: str):
    tag = tag.strip('#').upper().replace('O', '0')
    # Check invalid char
    for char in tag:
        if char not in VALID_TAG_CHARS:
            raise ValueError(f'Tag ({tag}) with invalid character(s) passed. Valid characters are {VALID_TAG_CHARS}')
    # Check len
    if len(tag) < 3:
        raise ValueError(f'Tag ({tag}) too short, expected min length 3')
    # Prepare for url
    if not tag.startswith('%23'):
        tag = f'%23{tag}'
    return tag


def filter_none_values(dictionary: dict):
    return {k: v for k, v in dictionary.items() if v is not None}
