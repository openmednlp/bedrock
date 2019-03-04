class Token:
    ID = 'id'
    BEGIN = 'begin'
    END = 'end'
    TEXT = 'text'
    SENT_START = 'is_sent_start'
    POS_VALUE = 'pos_value'
    DEP_TYPE = 'dependency_type'
    GOV_ID = 'governor_id'
    ENTITY = 'entity'

    COLS = [ID, BEGIN, END, TEXT, SENT_START, POS_VALUE, DEP_TYPE, GOV_ID, ENTITY]
