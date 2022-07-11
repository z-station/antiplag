class Lang:

    """ Содержит языковые константы. """

    CPP = 'cpp'
    PYTHON = 'python'
    JAVA = 'java'
    PASCAL = 'pascal'

    SIM_LANGS = CPP, JAVA, PASCAL

    CHOICES = (
        (CPP, CPP),
        (PYTHON, PYTHON),
        (JAVA, JAVA),
        (PASCAL, PASCAL)
    )

    VALUES = (CPP, JAVA, PASCAL, PYTHON)
