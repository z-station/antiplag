class Lang:

    """ Содержит языковые константы. """

    CPP = 'cpp'
    PYTHON = 'python'
    JAVA = 'java'

    SIM_LANGS = CPP, JAVA

    CHOICES = (
        (CPP, CPP),
        (PYTHON, PYTHON),
        (JAVA, JAVA)
    )
