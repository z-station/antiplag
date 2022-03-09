class Lang:

    """ Содержит языковые константы. """

    CPP = 'cpp'
    PYTHON = 'python'
    JAVA = 'java'

    SIM_LANGS = CPP, JAVA
    SIM_LANGS_JAVA = JAVA
    PYCODE_LANGS = PYTHON

    CHOICES = (
        (CPP, CPP),
        (PYTHON, PYTHON),
        (JAVA, JAVA)
    )
