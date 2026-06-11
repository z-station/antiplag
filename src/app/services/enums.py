

class Lang:

    """ Содержит языковые константы. """

    CPP = 'cpp'
    PYTHON = 'python'
    JAVA = 'java'
    SQL = 'sql'

    CHOICES = (
        (CPP, CPP),
        (PYTHON, PYTHON),
        (JAVA, JAVA),
        (SQL, SQL)
    )

    VALUES = (CPP, JAVA, PYTHON, SQL)
